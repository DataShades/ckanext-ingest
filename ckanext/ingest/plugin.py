from __future__ import annotations

import contextlib

import ckan.plugins.toolkit as tk
from ckan import common
from ckan import plugins as p

from . import config, interfaces, shared


@tk.blanket.auth_functions
@tk.blanket.actions
@tk.blanket.validators
@tk.blanket.cli
@tk.blanket.blueprints
@tk.blanket.config_declarations
class IngestPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IConfigurable)
    p.implements(interfaces.IIngest, inherit=True)

    # IConfigurer

    def update_config(self, config_: common.CKANConfig):
        tk.add_template_directory(config_, "templates")

    # IConfigurable

    def configure(self, config_: common.CKANConfig):
        shared.strategies.clear()

        whitelist = config.allowed_strategies()
        blacklist = config.disabled_strategies()
        name_mapping = config.name_mapping()

        for plugin in p.PluginImplementations(interfaces.IIngest):
            for name, s in plugin.get_ingest_strategies().items():
                final_name = name_mapping.get(f"{s.__module__}:{s.__name__}", name)

                if whitelist and final_name not in whitelist:
                    continue

                if final_name in blacklist:
                    continue

                shared.strategies.update({final_name: s})

    # IIngest
    def get_ingest_strategies(self) -> dict[str, type[shared.ExtractionStrategy]]:
        from .strategy import csv, zip

        strategies: dict[str, type[shared.ExtractionStrategy]] = {
            "ingest:recursive_zip": zip.ZipStrategy,
            "ingest:scheming_csv": csv.CsvStrategy,
        }

        with contextlib.suppress(ImportError):
            from .strategy.xlsx import XlsxStrategy

            strategies["ingest:xlsx"] = XlsxStrategy

        return strategies
