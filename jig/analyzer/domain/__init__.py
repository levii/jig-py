import dataclasses
from typing import List

from jig.analyzer.domain.dependency.module_dependency import ModuleDependency
from jig.collector.domain.source_code.source_code import SourceCode
from jig.collector.domain.values.module_path import ModulePath


@dataclasses.dataclass
class ModuleSpace:
    _module_path_set: List[ModulePath]

    def includes(self, module_path: ModulePath) -> bool:
        """
        指定されたModulePathがこのModule空間に含まれるモジュールかを返す。
        :param module_path:
        :return:
        """
        return any([module_path.belongs_to(p) for p in self._module_path_set])


@dataclasses.dataclass
class SourceCodeList:
    _source_codes: List[SourceCode]

    def all_dependencies(self) -> List[ModuleDependency]:
        result = []
        for source_code in self._source_codes:
            result += source_code.module_dependencies()

        return result

    def to_module_space(self) -> ModuleSpace:
        return ModuleSpace(
            _module_path_set=[
                source_code.module_path for source_code in self._source_codes
            ]
        )
