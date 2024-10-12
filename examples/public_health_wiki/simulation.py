import asyncio
from atlas.core.atlas import ATLAS
from atlas.core.entity import Entity, EntityFactory
from atlas.core.pattern import Pattern
from atlas.core.iquery import iQuery
from atlas.resources.openai_handler import OpenAIGPTHandler

# Define seed entities
# Seed entities
seed_entities = [
    {
        "entity_id": "Epidemiology",
        "attributes": {
            "name": "Epidemiology",
            "description": "The study of how diseases spread in populations",
            "references": ["Biostatistics", "Infectious_Disease_Control"]
        }
    },
    {
        "entity_id": "Environmental_Health",
        "attributes": {
            "name": "Environmental Health",
            "description": "The branch of public health concerned with environmental factors affecting human health",
            "references": ["Health_Policy", "Health_Promotion"]
        }
    },
    {
        "entity_id": "Health_Policy",
        "attributes": {
            "name": "Health Policy",
            "description": "Decisions, plans, and actions undertaken to achieve specific healthcare goals in a society",
            "references": ["Health_Promotion"]
        }
    },
    {
        "entity_id": "Infectious_Disease_Control",
        "attributes": {
            "name": "Infectious Disease Control",
            "description": "Measures to prevent and control the spread of infectious diseases",
            "references": ["Epidemiology", "Biostatistics"]
        }
    },
    {
        "entity_id": "Biostatistics",
        "attributes": {
            "name": "Biostatistics",
            "description": "The application of statistics to biological fields including public health",
            "references": ["Epidemiology"]
        }
    },
    {
        "entity_id": "Health_Promotion",
        "attributes": {
            "name": "Health Promotion",
            "description": "The process of enabling people to increase control over, and to improve, their health",
            "references": ["Environmental_Health", "Health_Policy"]
        }
    }
]


# Define patterns
patterns = [
    {
        "name": "PublicHealthDomain",
        "iqueries": [
            {
                "name": "Definition",
                "target_attribute": "definition",
                "prompt_template": "Provide a comprehensive definition of the public health domain: {name}"
            },
            {
                "name": "KeyCapabilities",
                "target_attribute": "key_capabilities",
                "prompt_template": "List and briefly describe 3-5 key capabilities within the {name} domain of public health"
            },
            {
                "name": "RelatedDomains",
                "target_attribute": "related_domains",
                "prompt_template": "Identify 2-3 closely related public health domains to {name} and explain their connections"
            },
            {
                "name": "HistoricalContext",
                "target_attribute": "historical_context",
                "prompt_template": "Provide a brief historical context for the development of {name} as a public health domain"
            }
        ]
    },
    {
        "name": "PublicHealthCapability",
        "iqueries": [
            {
                "name": "CapabilityDescription",
                "target_attribute": "description",
                "prompt_template": "Provide a detailed description of the public health capability: {name}"
            },
            {
                "name": "RequiredSkills",
                "target_attribute": "required_skills",
                "prompt_template": "List and briefly describe 3-5 key skills required for the {name} capability in public health"
            },
            {
                "name": "ApplicationScenarios",
                "target_attribute": "application_scenarios",
                "prompt_template": "Describe 2-3 real-world scenarios where the {name} capability is crucial in public health practice"
            },
            {
                "name": "TechnologicalTools",
                "target_attribute": "technological_tools",
                "prompt_template": "List and briefly describe 2-3 key technological tools or software commonly used in the {name} capability"
            }
        ]
    },
    {
        "name": "PublicHealthScenario",
        "iqueries": [
            {
                "name": "ScenarioImpact",
                "target_attribute": "impact",
                "prompt_template": "Describe the potential impact of the {name} scenario on public health systems and populations"
            },
            {
                "name": "RequiredResponses",
                "target_attribute": "required_responses",
                "prompt_template": "List and briefly describe 3-5 key public health responses required to address the {name} scenario"
            },
            {
                "name": "RelevantDomains",
                "target_attribute": "relevant_domains",
                "prompt_template": "Identify and explain the relevance of 3-4 public health domains that are critical in addressing the {name} scenario"
            }
        ]
    }
]

# Define simulation scenarios
simulation_scenarios = [
    {
        "name": "COVID-19 Pandemic",
        "description": "A global outbreak of a novel coronavirus",
        "focus_areas": ["Epidemiology", "Infectious_Disease_Control", "Health_Policy"]
    },
    {
        "name": "Climate Change Health Impact",
        "description": "Addressing health issues arising from global climate change",
        "focus_areas": ["Environmental_Health", "Health_Policy", "Health_Promotion"]
    },
    {
        "name": "Opioid Crisis",
        "description": "A widespread misuse of opioid drugs, including prescription painkillers and illicit drugs like heroin",
        "focus_areas": ["Health_Policy", "Health_Promotion", "Epidemiology"]
    },
    {
        "name": "Antimicrobial Resistance",
        "description": "The ability of microorganisms to resist the effects of drugs that once could successfully treat them",
        "focus_areas": ["Infectious_Disease_Control", "Health_Policy", "Biostatistics"]
    }
]

async def run_simulation():
    atlas = ATLAS()
    openai_handler = OpenAIGPTHandler()

    try:
        # Create patterns
        patterns_dict = {}
        for pattern_data in patterns:
            pattern = Pattern(pattern_data['name'])
            for iquery_data in pattern_data['iqueries']:
                iquery = iQuery(
                    iquery_data['name'],
                    iquery_data['target_attribute'],
                    [openai_handler]
                )
                pattern.add_iquery(iquery)
            patterns_dict[pattern_data['name']] = pattern

        # Create and register seed entities
        for entity_data in seed_entities:
            entity = EntityFactory.create_entity({
                **entity_data,
                'patterns': [patterns_dict['PublicHealthDomain']]
            })
            atlas.register_entity(entity)

        # Run initial update cycles
        print("Running initial update cycles...")

        # Start the global update cycle as a background task
        update_task = asyncio.create_task(atlas.global_update_cycle())

        # Allow some time for initial updates
        await asyncio.sleep(5)  # Adjust as needed

        # Proceed with introducing scenarios and other operations
        for scenario in simulation_scenarios:
            print(f"\nIntroducing scenario: {scenario['name']}")
            scenario_entity = EntityFactory.create_entity({
                'entity_id': scenario['name'],
                'patterns': [patterns_dict['PublicHealthCapability']],
                'attributes': scenario
            })
            atlas.register_entity(scenario_entity)

            # Allow updates to process the new scenario
            await asyncio.sleep(3)  # Adjust as needed

            print(f"Analysis after {scenario['name']}:")
            atlas.perform_graph_analysis()

            # Display updated knowledge base
            for entity in atlas.entities.values():
                print(f"\nEntity: {entity.entity_id}")
                print(f"Definition: {entity.attributes.get('definition', 'N/A')}")
                print(f"Relevance to {scenario['name']}: {entity.attributes.get('relevance', 'N/A')}")
                print(f"Authority: {entity.attributes.get('authority', 'N/A')}")

        # Optionally, cancel the background update task if no longer needed
        update_task.cancel()
        try:
            await update_task
        except asyncio.CancelledError:
            print("Global update cycle task cancelled.")

    finally:
        await openai_handler.close()

if __name__ == "__main__":
    asyncio.run(run_simulation())
