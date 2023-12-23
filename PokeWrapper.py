import os
import time

import Utils
from Resources import Move, Ability, Type, Version, Pokemon, Species
from Resources import VersionGroup, Generation

from rich.progress import track
from console import console

class PokeWrapper:
    BASE_URL = 'https://pokeapi.co/api/v2/'

    RESOURCES = {
        'Pokemon': Pokemon.Pokemon,
        'Ability': Ability.Ability,
        'Type': Type.Type,
        'Move': Move.Move,
        'Version': Version.Version,
        # 'Berry': Berry.Berry,
        # 'Location': Location.Location,
        # 'Item': Item.Item,
        'Species': Species.Species,
        'VersionGroup': VersionGroup.VersionGroup,
        'Generation': Generation.Generation
    }

    @classmethod
    def HandleSearch(cls, optionName):
        resource = cls.RESOURCES.get(optionName)
        if resource is not None:
            query = input(f'{optionName.title()} Name or ID: ').lower()
            if query is not '':
                with console.status("Querying..."):
                    result = resource.HandleSearch(query)
                if result is not None:
                    Utils.PrintData(result)
        else:
            print("Not a valid search!")

    @staticmethod
    def HandleCacheTest():
        print("Cache Test")
        for i in track(range(1, 10), description="Fetching generation data..."):
            Generation.Generation.HandleSearch(str(i))
            time.sleep(0.1)

        for i in track(range(1, 51), description="Fetching Pokemon data..."):
            Pokemon.Pokemon.HandleSearch(str(i))
            time.sleep(0.25)
        return

    @staticmethod
    def SaveCaches():
        if not os.path.exists(Utils.CACHE_DIR):
            os.makedirs(Utils.CACHE_DIR)
        for resource in PokeWrapper.RESOURCES.values():
            resource.SaveCache()

    @staticmethod
    def LoadCaches():
        for resource in PokeWrapper.RESOURCES.values():
            resource.LoadCache()
