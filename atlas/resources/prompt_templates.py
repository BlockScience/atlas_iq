from string import Template

class PromptTemplates:
    @staticmethod
    def get_definition_prompt(entity: 'Entity') -> str:
        """
        Generates a prompt for obtaining the definition of an entity.
        """
        template_str = (
            "As an expert in ${domain}, provide a detailed and precise definition of '${name}'. "
            "Include relevant context and examples where appropriate."
        )
        template = Template(template_str)
        context = entity.get_context()  # Assume this method provides additional context
        return template.substitute(name=entity.attributes.get('name'), domain=context.get('domain', 'the subject'))

