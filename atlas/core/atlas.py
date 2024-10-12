# atlas/core/atlas.py

import asyncio
import logging
from typing import Dict, Any
import networkx as nx
from .entity import Entity
from ..data.repository import Repository
from ..utils.config import config

logger = logging.getLogger(__name__)

class ATLAS:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ATLAS, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            self.repository = Repository()
            self.entities = {}
            self.global_state = {}
            self.update_interval = config.ATLAS_UPDATE_INTERVAL  # From config
            self.loop = asyncio.get_event_loop()
            self.initialized = True

    def register_entity(self, entity: Entity):
        print(f"Registering ENTITY: {entity.entity_id}")
        self.entities[entity.entity_id] = entity
        logger.debug(f"Entity '{entity.entity_id}' registered with ATLAS. Total entities: {len(self.entities)}")


    def unregister_entity(self, entity_id: str):
        if entity_id in self.entities:
            del self.entities[entity_id]
            logger.debug(f"Entity '{entity_id}' unregistered from ATLAS.")

    async def global_update_cycle(self):
        while True:
            logger.info("Starting global update cycle.")
            tasks = [
                entity.local_update(self.global_state)
                for entity in self.entities.values()
            ]
            await asyncio.gather(*tasks)
            logger.info("Global update cycle completed.")
            await asyncio.sleep(self.update_interval)

    def run(self):
        try:
            self.loop.run_until_complete(self.global_update_cycle())
        except KeyboardInterrupt:
            logger.info("ATLAS stopped by user.")
        finally:
            self.loop.close()

    async def trigger_dynamic_refactor(self):
        """
        Triggers dynamic refactoring of entities based on conditions.
        """
        logger.info("Triggering dynamic refactor.")
        for entity in self.entities.values():
            if self.should_refactor(entity):
                await entity.refactor(self.global_state)

    def should_refactor(self, entity):
        """
        Determines if an entity needs to be refactored.
        """
        return entity.requires_refactor()  # Method within Entity class

    async def manage_autopoiesis(self):
        """
        Manages autopoiesis by generating new entities and patterns.
        """
        logger.info("Managing autopoiesis.")
        for entity in self.entities.values():
            if entity.should_self_generate():
                new_entities = await entity.self_generate(self.global_state)
                for new_entity in new_entities:
                    self.register_entity(new_entity)

    async def global_update_cycle(self):
        """
        Global update cycle now includes dynamic refactoring and autopoiesis.
        """
        while True:
            logger.info("Starting global update cycle.")
            tasks = [entity.local_update(self.global_state) for entity in self.entities.values()]
            await asyncio.gather(*tasks)
            await self.trigger_dynamic_refactor()
            await self.manage_autopoiesis()
            logger.info("Global update cycle completed.")
            await asyncio.sleep(self.update_interval)

    def perform_graph_analysis(self):
        """
        Analyzes the graph structure and performs operations like authority smoothing.
        """
        G = nx.DiGraph()
        for entity in self.entities.values():
            G.add_node(entity.entity_id)
            for reference in entity.references:
                G.add_edge(entity.entity_id, reference)

        hub_scores, authority_scores = nx.hits(G)
        print("SCORES: ", authority_scores.items())
        print("ENTITIES: ", self.entities.items())
        for entity_id, authority in authority_scores.items():
            self.entities[entity_id].attributes['authority'] = authority

    async def smooth_authority(self):
        """
        Smooths authority values between entities in the graph.
        """
        self.perform_graph_analysis()
        min_authority = min(e.attributes['authority'] for e in self.entities.values())
        max_authority = max(e.attributes['authority'] for e in self.entities.values())

        for entity in self.entities.values():
            if entity.attributes['authority'] == min_authority:
                await entity.boost_authority(self.global_state)

    async def global_update_cycle(self):
        """
        Global update cycle now includes dynamic refactoring and autopoiesis.
        """
        while True:
            logger.info("Starting global update cycle.")
            entities_copy = list(self.entities.values())
            tasks = [entity.local_update(self.global_state) for entity in entities_copy]
            await asyncio.gather(*tasks)
            # await self.trigger_dynamic_refactor()
            # await self.manage_autopoiesis()
            # await self.smooth_authority()
            logger.info("Global update cycle completed.")
            await asyncio.sleep(self.update_interval)

