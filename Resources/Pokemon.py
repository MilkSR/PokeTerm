from bs4 import BeautifulSoup
import requests
import Utils
from Resources.Data import AbstractData
from Resources import Species, Ability, Generation, VersionGroup

from rich.table import Table
from rich import box
from console import console

# TODO: Override the search so if it fails to find a pokemon by the name, it searches for a species, then shows the default form


class Pokemon(AbstractData):
    ID_TO_NAME_CACHE = {}
    NAME_TO_DATA_CACHE = {}
    FLAGS = {
        'abilities'   : 1,
        'stats'       : 1,
        'availability': 1,
        'unavailable' : 1,
        'typing'      : 1,
    }
    ENDPOINT = 'pokemon'

    def __init__(self, data):
        super().__init__(data)

        # region Abilities
        self.possibleAbilities = []
        self.hiddenAbility = None
        abilityList: list = data.get('abilities')
        for ability in abilityList:
            newAbility = Ability.Ability.HandleSearch(ability.get('ability').get('name'))
            if newAbility is not None:
                if ability.get('is_hidden') is True:
                    self.hiddenAbility = newAbility
                else:
                    self.possibleAbilities.append(newAbility)
        # endregion

        # Species
        species = Species.Species.HandleSearch((data.get('species').get('name')))
        if species is not None:
            self.speciesID = species.ID

        # Stats
        self.baseStats = {}
        self.EVs = {}
        for stat in data.get('stats'):
            statName = stat.get('stat').get('name')
            self.baseStats[statName] = int(stat.get('base_stat'))
            self.EVs[statName] = int(stat.get('effort'))

        # Available Locations
        self.locationInformation = self.LocationLoader()

        # TODO: Surface link to shiny sprite
        self.shinyLink = data.get('sprites').get('other').get('official-artwork').get('front_shiny')

        # TODO:
        #   First Generation Appearance (Species)
        #   National Dex Number (Species)

        # TODO:
        #   List of moves (probably just in Gen 9 for right now)
        #   Evolution information (Looks like its own endpoint?)
        #   Other forms
        #   Type Effectiveness
        #       Make Type class do a thing

        self.types = [t.get('type').get('name') for t in data.get('types')]

    def PrintData(self):
        console.rule(self.name.title(), align='left')

        self.PrintTypeInfo()
        self.PrintBasicInfo()
        self.PrintAbilityInfo()
        self.PrintStatInfo()
        self.PrintVersionInfo()
        return

    def PrintBasicInfo(self):
        # self.PrintTypeInformation()
        console.print(f'[link={self.shinyLink}]Shiny Link (ctrl + click)[/]')
        species = Species.Species.HandleSearch(self.speciesID)
        if species is not None:
            species.PrintDataForPokemonPage()
        return

    def PrintTypeInfo(self) -> None:
        print()
        console.rule("[T]ype Information", align='left', characters=' ')
        if not self.FLAGS['typing']:
            return

        title = f'{self.FormattedTypeOne}{self.FormattedTypeTwo}'

        typeTable = Table(title=title, box=box.ROUNDED, title_justify='left', show_lines=True)

        typeTable.add_column("NOR", header_style='normal')
        typeTable.add_column("FIR", header_style='fire')
        typeTable.add_column("WAT", header_style='water')
        typeTable.add_column("ELE", header_style='electric')
        typeTable.add_column("GRA", header_style='grass')
        typeTable.add_column("ICE", header_style='ice')
        typeTable.add_column("FIG", header_style='fighting')
        typeTable.add_column("POI", header_style='poison')
        typeTable.add_column("GRO", header_style='ground')
        typeTable.add_column("FLY", header_style='flying')
        typeTable.add_column("PSY", header_style='psychic')
        typeTable.add_column("BUG", header_style='bug')
        typeTable.add_column("ROC", header_style='rock')
        typeTable.add_column("GHO", header_style='ghost')
        typeTable.add_column("DRA", header_style='dragon')
        typeTable.add_column("DAR", header_style='dark')
        typeTable.add_column("STE", header_style='steel')
        typeTable.add_column("FAI", header_style='fairy')

        typeTable.add_row("?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?")

        console.print(typeTable)

    def PrintAbilityInfo(self) -> None:
        print()
        console.rule("[P]ossible Abilities", align='left')
        if not self.FLAGS['abilities']:
            return

        abilityTable = Table(box=box.ROUNDED, show_lines=True)

        abilityTable.add_column("Ability")
        abilityTable.add_column("Description")

        for ability in self.possibleAbilities:
            abilityTable.add_row(f"[bold]{ability.name.title()}[/]", ability.description)
        if self.hiddenAbility is not None:
            abilityTable.add_row(f"[bold]{self.hiddenAbility.name.title()} (H)[/]", self.hiddenAbility.description)
        console.print(abilityTable)

    # Don't care about hardcoding, this is way more readable
    def PrintStatInfo(self) -> None:
        print()
        console.rule("[S]tat Information", align='left')
        if not self.FLAGS['stats']:
            return

        statsTable = Table(box=box.ROUNDED)

        statsTable.add_column("HP", header_style="hp")
        statsTable.add_column("Attack", header_style="attack")
        statsTable.add_column("Defense", header_style="defense")
        statsTable.add_column("Sp Atk", header_style="special-attack")
        statsTable.add_column("Sp Def", header_style="special-defense")
        statsTable.add_column("Speed", header_style="speed")
        statsTable.add_column("Total")

        statsTable.add_row(str(self.baseStats['hp']), str(self.baseStats['attack']),
                           str(self.baseStats['defense']), str(self.baseStats['special-attack']),
                           str(self.baseStats['special-defense']), str(self.baseStats['speed']),
                           str(sum(self.baseStats.values())))

        console.print(statsTable)

        outputStr = '[bold]EV Yield:[/] '
        if self.EVs['hp'] != 0:
            outputStr += f"[hp]{str(self.EVs['hp'])} HP[/hp], "
        if self.EVs['attack'] != 0:
            outputStr += f"[attack]{str(self.EVs['attack'])} Attack[/attack], "
        if self.EVs['defense'] != 0:
            outputStr += f"[defense]{str(self.EVs['defense'])} Defense[/defense], "
        if self.EVs['special-attack'] != 0:
            outputStr += f"[special-attack]{str(self.EVs['special-attack'])} Sp. Attack[/special-attack], "
        if self.EVs['special-defense'] != 0:
            outputStr += f"[special-defense]{str(self.EVs['special-defense'])} Sp. Defense[/special-defense], "
        if self.EVs['speed'] != 0:
            outputStr += f"[speed]{str(self.EVs['speed'])} Speed[/speed], "

        console.print(outputStr[:-2])

    def PrintVersionInfo(self) -> None:
        print()
        if not self.FLAGS['availability']:
            print("[A]vailability Info")
            return

        available, unavailable = [], []
        if self.locationInformation is None:
            return
        for game in self.locationInformation.keys():
            locations = self.locationInformation[game]
            if len(locations) == 0:
                unavailable.append(game)
            else:
                available.append(game)

        overallInfoTable = Table(title="[A]vailability Info", title_justify="left", box=box.HORIZONTALS, show_header=False, show_lines=True)

        overallInfoTable.add_column()
        overallInfoTable.add_column()
        overallInfoTable.add_column()

        overallInfoTable.add_row(self.GetGenerationTable(1), self.GetGenerationTable(2), self.GetGenerationTable(3))
        overallInfoTable.add_row(self.GetGenerationTable(4), self.GetGenerationTable(5), self.GetGenerationTable(6))
        overallInfoTable.add_row(self.GetGenerationTable(7), self.GetGenerationTable(8), self.GetGenerationTable(9))

        # TODO: Eventually implement an "ignore certain generations" flag

        console.print(overallInfoTable)

    def GetGenerationTable(self, gen):
        genTable = Table(title=f"Generation {gen}")
        genTable.add_column("Game")
        genTable.add_column("Location")
        genInfo = Generation.Generation.HandleSearch(gen)
        for versionGroup in genInfo.versionGroups:
            groupInfo = VersionGroup.VersionGroup.HandleSearch(versionGroup)
            for version in groupInfo.versions:
                versionLocations = self.locationInformation.get(version)
                if versionLocations is None or len(versionLocations) == 0:
                    continue
                secondCell = ", ".join(versionLocations)
                genTable.add_row(f'[{version}]{Utils.REVERSED_MAPPING_DICT[version]}[/]', secondCell)
        return genTable

    def LocationLoader(self) -> dict[str, list[str]] | None:  # eventually dict[int, list[int]] for IDs instead
        queryURL = f"https://pokemondb.net/pokedex/{self.name}"
        response = requests.get(queryURL)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the table with location information
        locationsDiv = soup.find('div', {'id': 'dex-locations'})

        locationsTable = ''

        # Find the first table after the 'dex-locations' div
        if locationsDiv:
            locationsTable = locationsDiv.find_next('table')

        # Assuming 'location_table' is the BeautifulSoup object for the table
        locationRows = locationsTable.find_all('tr')

        encounters = {}
        for row in locationRows:
            games = []
            locations = []
            gamesHTML = row.find_next('th')
            for game in gamesHTML.find_all('span'):
                games.append(game.text)
            locationsHTML = row.find_next('td')
            for location in locationsHTML.find_all('a'):
                locations.append(location.text)

            for gameName in games:
                encounters[Utils.VERSION_MAPPING_DICT[gameName]] = locations

        return encounters

    @property
    def FormattedTypeOne(self) -> str:
        return f'[{self.types[0]}]{self.types[0].title()}[/]'

    @property
    def FormattedTypeTwo(self) -> str:
        if len(self.types) < 2:
            return ""
        return f' / [{self.types[1]}]{self.types[1].title()}[/]'

    # endregion

    def AddToCache(self):
        super().AddToCache()

    @classmethod
    def ToggleFlag(cls, flag: str):
        match flag:
            case 'p':
                cls.FLAGS['abilities'] = not cls.FLAGS['abilities']
            case 's':
                cls.FLAGS['stats'] = not cls.FLAGS['stats']
            case 'a':
                cls.FLAGS['availability'] = not cls.FLAGS['availability']
            case 'u':
                cls.FLAGS['unavailable'] = not cls.FLAGS['unavailable']
            case 't':
                cls.FLAGS['typing'] = not cls.FLAGS['typing']
            case _:
                return
