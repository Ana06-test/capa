# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
# You may obtain a copy of the License at: [package root]/LICENSE.txt
# Unless required by applicable law or agreed to in writing, software distributed under the License
#  is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import idaapi

import capa.features.extractors.ida.file
import capa.features.extractors.ida.insn
import capa.features.extractors.ida.function
import capa.features.extractors.ida.basicblock
from capa.features.extractors import FeatureExtractor


class FunctionHandle:
    """this acts like an idaapi.func_t but with __int__()"""

    def __init__(self, inner):
        self._inner = inner

    def __int__(self):
        return self.start_ea

    def __getattr__(self, name):
        return getattr(self._inner, name)


class BasicBlockHandle:
    """this acts like an idaapi.BasicBlock but with __int__()"""

    def __init__(self, inner):
        self._inner = inner

    def __int__(self):
        return self.start_ea

    def __getattr__(self, name):
        return getattr(self._inner, name)


class InstructionHandle:
    """this acts like an idaapi.insn_t but with __int__()"""

    def __init__(self, inner):
        self._inner = inner

    def __int__(self):
        return self.ea

    def __getattr__(self, name):
        return getattr(self._inner, name)


class IdaFeatureExtractor(FeatureExtractor):
    def __init__(self):
        super(IdaFeatureExtractor, self).__init__()

    def get_base_address(self):
        return idaapi.get_imagebase()

    def extract_file_features(self):
        for (feature, ea) in capa.features.extractors.ida.file.extract_features():
            yield feature, ea

    def get_functions(self):
        import capa.features.extractors.ida.helpers as ida_helpers

        # data structure shared across functions yielded here.
        # useful for caching analysis relevant across a single workspace.
        ctx = {}

        # ignore library functions and thunk functions as identified by IDA
        for f in ida_helpers.get_functions(skip_thunks=True, skip_libs=True):
            setattr(f, "ctx", ctx)
            yield FunctionHandle(f)

    @staticmethod
    def get_function(ea):
        f = idaapi.get_func(ea)
        setattr(f, "ctx", {})
        return FunctionHandle(f)

    def extract_function_features(self, f):
        for (feature, ea) in capa.features.extractors.ida.function.extract_features(f):
            yield feature, ea

    def get_basic_blocks(self, f):
        import capa.features.extractors.ida.helpers as ida_helpers

        for bb in ida_helpers.get_function_blocks(f):
            yield BasicBlockHandle(bb)

    def extract_basic_block_features(self, f, bb):
        for (feature, ea) in capa.features.extractors.ida.basicblock.extract_features(f, bb):
            yield feature, ea

    def get_instructions(self, f, bb):
        import capa.features.extractors.ida.helpers as ida_helpers

        for insn in ida_helpers.get_instructions_in_range(bb.start_ea, bb.end_ea):
            yield InstructionHandle(insn)

    def extract_insn_features(self, f, bb, insn):
        for (feature, ea) in capa.features.extractors.ida.insn.extract_features(f, bb, insn):
            yield feature, ea
