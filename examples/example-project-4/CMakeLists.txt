# This file was generated by Xen ProjGen.
# File: CMakeLists.txt
# Version: 1.0
# Author: XeniaPhe
# License: MIT License
# Github: https://github.com/XeniaPhe/Xen-ProjGen
# Description: Configures the build system for the project, defining targets, dependencies and settings

cmake_minimum_required(VERSION 3.15...3.30)
include("${CMAKE_SOURCE_DIR}/utils/functions.cmake")

project(example-project-4 VERSION 0.1.0 LANGUAGES C CXX)
set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(TARGET "program")

# Make a list of useful preprocessor definitions to add to the build
set(DEFS "")
get_compiler_definition(COMPILER_DEFINITION)
get_compiler_variant(${COMPILER_DEFINITION} COMPILER_VARIANT)
list(APPEND DEFS "${COMPILER_DEFINITION}")
append_architectural_definitions(DEFS)
append_os_definitions(DEFS)
append_build_definitions(DEFS)

# Also add the user defined definitions to the list
read_file("${CMAKE_SOURCE_DIR}/config/definitions.txt" USER_DEFS)
list(APPEND DEFS "${USER_DEFS}")

# Get the compiler flags for the target compiler
get_compiler_flags(${COMPILER_VARIANT} FLAGS)

# Get the compiler features
read_file("${CMAKE_SOURCE_DIR}/config/compiler_features.txt" FEATURES)

# Get the link options
read_file("${CMAKE_SOURCE_DIR}/config/linker_flags.txt" LINKER_FLAGS)

set(SOURCE_ROOT "${CMAKE_SOURCE_DIR}/example-project-4/")

file(GLOB LINK_LIBS "${SOURCE_ROOT}/libs/*/lib/*.a" "${SOURCE_ROOT}/libs/*/lib/*.lib")
file(GLOB DY_LIBS "${SOURCE_ROOT}/libs/*/lib/*.so" "${SOURCE_ROOT}/libs/*/lib/*.dll" "${SOURCE_ROOT}/libs/*/lib/*.dylib")
file(GLOB INCLUDE_DIRS "${SOURCE_ROOT}/libs/*/include")
file(GLOB_RECURSE HEADERS "${SOURCE_ROOT}/include/*.h" "${SOURCE_ROOT}/include/*.hpp")
file(GLOB_RECURSE SOURCE "${SOURCE_ROOT}/src/*.c" "${SOURCE_ROOT}/src/*.cpp")

list(APPEND INCLUDE_DIRS "${SOURCE_ROOT}/include")

add_exec_target("${TARGET}" "${SOURCE}" "${HEADERS}" "${INCLUDE_DIRS}" "${LINK_LIBS}" "${DY_LIBS}" "${DEFS}" "${FLAGS}" "${FEATURES}" "${LINKER_FLAGS}" FALSE)