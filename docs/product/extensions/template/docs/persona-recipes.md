# Persona recipes

> Replace this template if the extension is meant to be paired with
> specific personas. Delete the file otherwise.

The extension does not create personas — personas are user identity, owned
by the user. But the extension can *recommend* briefings and routing
keywords that pair well with its capabilities.

For each suggested persona, document:

- **Persona id.** What name to use in the user's identity.
- **Inherits from.** `self` or `ego`.
- **Briefing.** A copy-pasteable block of text the user can drop into
  their persona YAML or seed into the database.
- **Routing keywords.** Suggested list. The user merges with their own.
- **What this persona does.** When it should be routed.
- **How it pairs with this extension.** Which capability it should bind
  to, and why.

Always say clearly: **the user adapts these recipes. They are not
prescriptive.** A user with their own `cfo` persona may bind the same
capability there instead; both choices are valid.

End with a worked example showing the full sequence:

1. Seeding the persona.
2. Installing the extension.
3. Binding the capability.
4. A sample Mirror Mode turn showing the result.
