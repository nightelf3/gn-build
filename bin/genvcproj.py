import json
import sys
import uuid
import re

from pprint import pprint

def FillPath(sources, paths):
  paths = list(filter(lambda x: x != "", paths))
  filename = paths.pop()
  path = "\\".join(paths)
  if path not in sources:
    sources[path] = []
  sources[path].append(filename)
  return sources

def GetSources(json):
  sources = {}
  if (json == None):
    return sources

  for key, target in json["targets"].items():
    if "sources" not in target:
      continue
    for file in target["sources"]:
      sources = FillPath(sources, re.split("/+", file))
  return sources

def GetDefines(json):
  defines = []
  if (json == None):
    return defines

  for key, target in json["targets"].items():
    if "defines" not in target:
      continue
    for define in target["defines"]:
      defines.append(define)
  return defines

def GetIncludes(json):
  includes = []
  if (json == None):
    return includes

  for key, target in json["targets"].items():
    if "includes" not in target:
      continue
    for include in target["include_dirs"]:
      includes.append(include)
  return includes

def WriteProject(file, sources, defines, includes):
  project = open(file + ".vcxproj", "w+")
  debug_defines = ";".join(defines)
  debug_includes = ";".join(includes)
  project.write('''<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup Label="ProjectConfigurations">
    <ProjectConfiguration Include="Debug|x64">
      <Configuration>Debug</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Release|x64">
      <Configuration>Release</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
  </ItemGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'" Label="Configuration">
    <ConfigurationType>Makefile</ConfigurationType>
    <UseDebugLibraries>true</UseDebugLibraries>
    <PlatformToolset>v142</PlatformToolset>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|x64'" Label="Configuration">
    <ConfigurationType>Makefile</ConfigurationType>
    <UseDebugLibraries>false</UseDebugLibraries>
    <PlatformToolset>v142</PlatformToolset>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />
  <ImportGroup Label="ExtensionSettings">
  </ImportGroup>
  <ImportGroup Label="Shared">
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Debug|x64'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Release|x64'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>
  <PropertyGroup Label="UserMacros" />
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'">
    <NMakeBuildCommandLine>ninja -C out/Debug</NMakeBuildCommandLine>
    <NMakeOutput>out/Debug/FirstSkiaApp.exe</NMakeOutput>
    <NMakeCleanCommandLine>del /s /q out</NMakeCleanCommandLine>
    <NMakeReBuildCommandLine>gn gen out/Debug</NMakeReBuildCommandLine>
    <NMakePreprocessorDefinitions>''' + debug_defines + ''';$(NMakePreprocessorDefinitions)</NMakePreprocessorDefinitions>
    <IncludePath>''' + debug_includes + ''';$(VC_IncludePath);$(WindowsSDK_IncludePath);</IncludePath>
    <IntDir>out\$(Configuration)\</IntDir>
    <OutDir>$(SolutionDir)\out\$(Configuration)\</OutDir>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|x64'">
    <NMakeBuildCommandLine>ninja -C out/Release</NMakeBuildCommandLine>
    <NMakeOutput>out/Release/FirstSkiaApp.exe</NMakeOutput>
    <NMakeCleanCommandLine>del /s /q out/Release</NMakeCleanCommandLine>
    <NMakeReBuildCommandLine>gn gen out/Release --args="is_debug=false"</NMakeReBuildCommandLine>
    <NMakePreprocessorDefinitions>''' + debug_defines + ''';$(NMakePreprocessorDefinitions)</NMakePreprocessorDefinitions>
    <IncludePath>''' + debug_includes + ''';$(VC_IncludePath);$(WindowsSDK_IncludePath);</IncludePath>
    <IntDir>out\$(Configuration)\</IntDir>
    <OutDir>$(SolutionDir)\out\$(Configuration)\</OutDir>
  </PropertyGroup>
  <ItemDefinitionGroup>
  </ItemDefinitionGroup>
  <ItemGroup>
''')
  for path, files in sources.items():
    for filename in files:
      project.write('      <ClCompile Include="{}" />\n'.format(path + "\\" + filename))
  project.write('''  </ItemGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />
  <ImportGroup Label="ExtensionTargets">
  </ImportGroup>
</Project>''')

def WriteFilters(file, sources):
  filters = open(file + ".vcxproj.filters", "w+")
  filters.write('''<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>\n''')
  for path in sources:
    filters.write('''      <Filter Include="''' + path + '''">
        <UniqueIdentifier>{''' + str(uuid.uuid4()) + '''}</UniqueIdentifier>
      </Filter>\n''')
  filters.write('''  </ItemGroup>
  <ItemGroup>''')
  
  for path, files in sources.items():
    for filename in files:
      filters.write('''    <ClCompile Include="{}">
        <Filter>{}</Filter>
      </ClCompile>\n'''.format(path + "\\" + filename, path))
  
  filters.write('''  </ItemGroup>
</Project>''')

def main():
  if len(sys.argv) != 2:
    print('Usage: ' + sys.argv[0] + ' <json_file_name>')
    exit(1)

  json_data = None
  with open(sys.argv[1], 'r') as json_file:
    json_data = json.loads(json_file.read())

  sources = GetSources(json_data)
  file = "project"
  WriteProject(file, sources, GetDefines(json_data), GetIncludes(json_data))
  WriteFilters(file, sources)

if __name__ == "__main__":
  main()