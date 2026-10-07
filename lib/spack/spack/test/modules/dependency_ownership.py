# Copyright Spack Project Developers. See COPYRIGHT file for details.
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from types import SimpleNamespace

import pytest

import spack.modules.common as common


@pytest.mark.parametrize("system", ["lmod", "tcl"])
def test_owner_names_and_exclusions(monkeypatch, system):
    """Parent projections and exclusions apply only to inherited Lmod dependencies."""
    specs = [SimpleNamespace(dag_hash=lambda h=h: h, installed_upstream=False)
             for h in ("parent", "excluded", "child")]
    monkeypatch.setattr(common, "dependency_ownership",
                        lambda: {"parent": "libyaml/0.2.5", "excluded": None})
    conf = SimpleNamespace(
        module_system=system, name="default", conf={"autoload": specs},
        make_configuration=lambda spec, name: SimpleNamespace(excluded=False),
        make_layout=lambda spec, name: SimpleNamespace(use_name=spec.dag_hash() + "-child"),
    )
    selected = common.BaseConfiguration._create_list_for(conf, "autoload")
    conf.specs_to_load = selected
    names = common.BaseContext._create_module_list_of(SimpleNamespace(conf=conf), "specs_to_load")
    assert names == (["libyaml/0.2.5", "child-child"] if system == "lmod"
                     else ["parent-child", "excluded-child", "child-child"])
