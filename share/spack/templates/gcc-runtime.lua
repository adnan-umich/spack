{% extends "modules/modulefile.lua" %}

{% block footer %}
{{ super() }}

-- Site customization:
-- Loading gcc-runtime also activates the matching GCC compiler hierarchy.
depends_on("gcc/{{ spec.version }}")

{% endblock %}
