import sys
import os
import re
import subprocess
from typing import List
from collections import namedtuple

ProjectConfig = namedtuple('ProjectConfig', [
    'proj_name',
    'target_name',
    'target_type',
    'use_c',
    'c_std',
    'use_cpp',
    'cpp_std',
    'should_list_h_files',
    'should_gen_include_dir',
    'is_include_dir_inside_src',
    'should_include_tests',
    'has_proj_name_dir',
    'should_gen_vscode_files',
    'should_gen_workspace_file',
    'should_add_src_and_include_dirs_to_ws',
    'has_proj_dir',
    'is_out_in_build_dir',
    'should_gen_readme',
    'should_init_git',
    'should_commit_git'
])

def message(msg: str):
    print(f'## {msg}')

def warning(msg: str):
    print(f'##! {msg}')

def get_input(msg: str) -> str:
    while True:
        try:
            response = input(f'>> {msg}')
        except EOFError:
            sys.exit(1)

        if response:
            return response
        else:
            warning('Input cannot be empty, please try again.')

def yes_or_no(msg: str) -> bool:
    response = get_input(msg + ' (y/n): ')
    return response.lower() == 'y'

def choose_one_of(msg: str, choices: List[str]) -> str:
    msg += ' ('
    for index, choice in enumerate(choices, start=1):
        msg += f'{choice} = {index}, '

    msg = msg[:-2] + '): '

    while True:
        response = get_input(msg)
        if response.isdigit():
            index = int(response) - 1
            if 0 <= index < len(choices):
                return choices[index]
            
        warning('Invalid choice, please try again.')

def sanitize_file_name(name: str, is_target: bool = False) -> str:
    sanitized_name = re.sub(r'[^a-zA-Z0-9._-' + f'{'+' if is_target else ''}]', '-', name)
    sanitized_name = re.sub(r'\s+', '-', sanitized_name).strip('-')
    sanitized_name = re.sub(r'-+', '-', sanitized_name)

    if is_target:
        sanitized_name = re.sub(r'\++', '+', sanitized_name).strip('+')

    if sanitized_name and sanitized_name[0].isdigit():
        sanitized_name = '_' + sanitized_name

    if len(sanitized_name) > 255:
        sanitized_name = sanitized_name[:255]

    reserved_names = {"","CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4",
                      "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", 
                      "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}

    if not is_target:
        reserved_names.update({'src', 'include', 'test', 'libs', 'build', 'out', 'project',
                               'config', 'utils', '.vscode', '.git'})
    
    if sanitized_name.upper() in reserved_names:
        sanitized_name = '_' + sanitized_name

    return sanitized_name

def gen_dir(cwd: str, dir_name: str) -> str:
    dir_path = os.path.join(cwd, dir_name)
    os.mkdir(dir_path)
    return dir_path

def gen_file(cwd: str, file_name: str, content: str) -> str:
    file_path = os.path.join(cwd, file_name)

    try:
        with open(file_path, 'w') as file:
            file.write(content)
    except Exception as e:
        print(f'Error creating file {file_path}: {e}')
        sys.exit(4)
    
    return file_path

def gen_vscode_dir(cwd: str, conf: ProjectConfig):
    if not conf.should_gen_vscode_files:
        return
    
    settings_json = """{
    "cmake.sourceDirectory": ["${workspaceFolder}"],
    "cmake.buildDirectory": "${workspaceFolder}/build",
    "cmake.preferredGenerators": [
            "Ninja",
            "Unix Makefiles",
            "Visual Studio 17 2022"
        ],
    "cmake.debugConfig": {
        "args": [],
    }
}"""

    tasks_json = """{
    "version": "2.0.0",
    "tasks": []
}"""

    launch_json = """{
    "version": "0.2.0",
    "configurations": [   
        {
            "name": "gdb-debug",
            "type": "cppdbg",
            "request": "launch",
            "program": "${command:cmake.launchTargetPath}",
            "args": [],
            "stopAtEntry": false,
            "cwd": "{[(CWD)]}",
            "environment": [
                {
                    "name": "PROJECT_PATH",
                    "value": "${env:PROJECT_PATH}:${command:cmake.getLaunchTargetDirectory}"
                }
            ],
            "externalConsole": true,
            "MIMode": "gdb",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ]
        },
        {
            "name": "lldb-debug",
            "type": "cppdbg",
            "request": "launch",
            "program": "${command:cmake.launchTargetPath}",
            "args": [],
            "stopAtEntry": false,
            "cwd": "{[(CWD)]}",
            "environment": [
                {
                    "name": "PROJECT_PATH",
                    "value": "${env:PROJECT_PATH}:${command:cmake.getLaunchTargetDirectory}"
                }
            ],
            "externalConsole": true,
            "MIMode": "lldb"
        },
        {
            "name": "msvc-debug",
            "type": "cppvsdbg",
            "request": "launch",
            "program": "${command:cmake.launchTargetPath}",
            "args": [],
            "stopAtEntry": false,
            "cwd": "{[(CWD)]}",
            "environment": [
                {
                    "name": "PROJECT_PATH",
                    "value": "${env:PROJECT_PATH}:${command:cmake.getLaunchTargetDirectory}"
                }
            ],
            "externalConsole": true
        },
        {
            "name": "ctest-launch",
            "type": "cppvsdbg",
            "request": "launch",
            "program": "${command:cmake.launchTargetPath}",
            "args": [],
            "stopAtEntry": false,
            "cwd": "{[(CWD)]}",
            "environment": [
                {
                    "name": "PROJECT_PATH",
                    "value": "${env:PROJECT_PATH}:${command:cmake.getLaunchTargetDirectory}"
                }
            ],
            "externalConsole": true
        },
        {
            "name": "ctest-debug",
            "type": "cppdbg",
            "request": "launch",
            "cwd": "{[(CWD)]}",
            "program": "${cmake.testProgram}",
            "args": [ "${cmake.testArgs}"],
        },
        {
            "name": "ctest-msvc-debug",
            "type": "cppvsdbg",
            "request": "launch",
            "cwd": "{[(CWD)]}",
            "program": "${cmake.testProgram}",
            "args": [ "${cmake.testArgs}"],
        }
    ]
}"""

    bin_dir = '${workspaceFolder}/build/out/bin' if conf.is_out_in_build_dir else '${workspaceFolder}/out/bin'
    launch_json = launch_json.replace('{[(CWD)]}', bin_dir)

    vscode_dir = gen_dir(cwd, '.vscode')
    gen_file(vscode_dir, 'launch.json', launch_json)
    gen_file(vscode_dir, 'tasks.json', tasks_json)
    gen_file(vscode_dir, 'settings.json', settings_json)

def gen_build_dir(cwd: str, conf: ProjectConfig):
    build_dir = gen_dir(cwd, 'build')
    out_dir = gen_dir(build_dir, 'out') if conf.is_out_in_build_dir else gen_dir(cwd, 'out')
    bin_dir = gen_dir(out_dir, 'bin')
    gen_dir(bin_dir, 'Debug')
    gen_dir(bin_dir, 'Release')
    lib_dir = gen_dir(out_dir, 'lib')
    gen_dir(lib_dir, 'Debug')
    gen_dir(lib_dir, 'Release')

    if conf.should_include_tests:
        test_dir = gen_dir(out_dir, 'test')
        gen_dir(test_dir, 'Debug')
        gen_dir(test_dir, 'Release')

def gen_utils_dir(cwd: str, conf: ProjectConfig):
    fetch_flags_py = r"""# This file was generated by Xen ProjGen.
# File: fetch_flags.py
# Version: 1.0
# Author: XeniaPhe
# License: MIT License
# Github: https://github.com/XeniaPhe/Xen-ProjGen
# Description: Parses the compiler_flags.yaml file and retrieves the flags for CMake

import re
import sys

if len(sys.argv) != 3:
    print("Usage: script.py <compiler> <build_type>", file = sys.stderr)
    sys.exit(1)

target_compiler = sys.argv[1].lower()
target_build_type = sys.argv[2].lower()

file_content = ""
try:
    with open("../config/compiler_flags.yaml", 'r') as file:
        file_content = file.read()
except FileNotFoundError:
    print("The file compiler_flags.yaml not found!")
except IOError as e:
    print(f"An I/O error occurred while accessing compiler_flags.yaml:\n {e}")
except Exception as e:
    print(f"An unexpected error occurred:\n {e}")

flags = []
current_compiler = None
current_build_type = None
current_flag = None

# Regex patterns to identify sections and flag details
compiler_pattern = re.compile(r'^\s*(gcc|clang|msvc):', re.IGNORECASE)
build_type_pattern = re.compile(r'^\s*(debug|release|minsizerel|relwithdebinfo):', re.IGNORECASE)
flag_pattern = re.compile(r'^\s*- flag: "(.*)"')
enabled_pattern = re.compile(r'^\s*enabled: (true|false)')

lines = file_content.splitlines()

for line in lines:
    # Skip comments or empty lines
    if not line.strip() or line.strip().startswith('#'):
        continue
    
    # Detect the compiler section (gcc, clang, msvc)
    compiler_match = compiler_pattern.match(line)
    if compiler_match:
        # Break out if all the requested data has been processed
        if current_compiler == target_compiler:
            break

        current_compiler = compiler_match.group(1).lower()
        continue

    if current_compiler != target_compiler:
        continue
    
    # Detect the build type (debug, release)
    build_type_match = build_type_pattern.match(line)
    if build_type_match:
        # Break out if all the requested data has been processed
        if current_build_type == target_build_type:
            break

        current_build_type = build_type_match.group(1).lower()
        continue

    if current_build_type != target_build_type:
        continue
    
    # Parse flags and enabled status
    if not current_flag:
        flag_match = flag_pattern.match(line)
        if flag_match:
            current_flag = flag_match.group(1)

        continue
    
    enabled_match = enabled_pattern.match(line)
    if enabled_match:
        if enabled_match.group(1).lower() == "true":
            flags.append(current_flag)

        current_flag = None

cmake_flags = ";".join(flags).strip()
print(cmake_flags)"""

    functions_cmake = r"""# This file was generated by Xen ProjGen.
# File: functions.cmake
# Version: 1.0
# Author: XeniaPhe
# License: MIT License
# Github: https://github.com/XeniaPhe/Xen-ProjGen
# Description: Provides the helper CMake functions

function(get_compiler_definition OUT_DEFINITION)
    if (CMAKE_CXX_COMPILER_ID)
        set(COMPILER_ID "${CMAKE_CXX_COMPILER_ID}")
    elseif (CMAKE_C_COMPILER_ID)
        set(COMPILER_ID "${CMAKE_C_COMPILER_ID}")
    else()
        message(FATAL_ERROR "No C or C++ compiler found.")
    endif()

    if ("${COMPILER_ID}" STREQUAL "GNU")
        set(${OUT_DEFINITION} "GCC_COMPILER" PARENT_SCOPE)
    elseif ("${COMPILER_ID}" STREQUAL "Clang")
        if ("${CMAKE_CXX_COMPILER_FRONTEND_VARIANT}" STREQUAL "MSVC")
            set(${OUT_DEFINITION} "CLANG_CL_COMPILER" PARENT_SCOPE)
        else()
            set(${OUT_DEFINITION} "CLANG_COMPILER" PARENT_SCOPE)
        endif()
    elseif ("${COMPILER_ID}" STREQUAL "MSVC")
        set(${OUT_DEFINITION} "MSVC_COMPILER" PARENT_SCOPE)
    else()
        set(${OUT_DEFINITION} "UNKNOWN_COMPILER" PARENT_SCOPE)
    endif()
endfunction()

function (get_compiler_variant COMPILER_DEFINITON OUT_VARIANT)
    if ("${COMPILER_DEFINITON}" STREQUAL "MSVC_COMPILER" OR "${COMPILER_DEFINITON}" STREQUAL "CLANG_CL_COMPILER")
        set(${OUT_VARIANT} "MSVC" PARENT_SCOPE)
    elseif ("${COMPILER_DEFINITON}" STREQUAL "GCC_COMPILER")
        set(${OUT_VARIANT} "GCC" PARENT_SCOPE)
    elseif ("${COMPILER_DEFINITON}" STREQUAL "CLANG_COMPILER")
        set(${OUT_VARIANT} "CLANG" PARENT_SCOPE)
    else()
        set(${OUT_VARIANT} "UNKNOWN" PARENT_SCOPE)
    endif()
endfunction()

function (append_architectural_definitions OUT_DEFINITIONS)
    if (CMAKE_SIZEOF_VOID_P EQUAL 8)
        list(APPEND ${OUT_DEFINITIONS} "WORD_SIZE_64")
    else()
        list(APPEND ${OUT_DEFINITIONS} "WORD_SIZE_32")
    endif()

    set(${OUT_DEFINITIONS} "${${OUT_DEFINITIONS}}" PARENT_SCOPE)
endfunction()

function (append_os_definitions OUT_DEFINITIONS)
    if ("${CMAKE_SYSTEM_NAME}" STREQUAL "Windows")
        list(APPEND ${OUT_DEFINITIONS} "WINDOWS")
    elseif ("${CMAKE_SYSTEM_NAME}" STREQUAL "Linux")
        list(APPEND ${OUT_DEFINITIONS} "LINUX")
        list(APPEND ${OUT_DEFINITIONS} "UNIX")
    elseif ("${CMAKE_SYSTEM_NAME}" STREQUAL "Darwin")
        list(APPEND ${OUT_DEFINITIONS} "MACOS")
        list(APPEND ${OUT_DEFINITIONS} "UNIX")
    else()
        list(APPEND ${OUT_DEFINITIONS} "OTHER_OS")
    endif()

    set(${OUT_DEFINITIONS} "${${OUT_DEFINITIONS}}" PARENT_SCOPE)
endfunction()

function (append_build_definitions OUT_DEFINITIONS)
    if ("${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
        list(APPEND ${OUT_DEFINITIONS} "DEBUG")
    elseif ("${CMAKE_BUILD_TYPE}" STREQUAL "Release")
        list(APPEND ${OUT_DEFINITIONS} "RELEASE")
    elseif ("${CMAKE_BUILD_TYPE}" STREQUAL "MinSizeRel")
        list(APPEND ${OUT_DEFINITIONS} "MINSIZEREL")
    elseif ("${CMAKE_BUILD_TYPE}" STREQUAL "RelWithDebInfo")
        list(APPEND ${OUT_DEFINITIONS} "RELWITHDEBINFO")
    endif()

    set(${OUT_DEFINITIONS} "${${OUT_DEFINITIONS}}" PARENT_SCOPE)
endfunction()

function(read_file FILE_PATH OUT_CONTENTS)
    file(READ "${FILE_PATH}" FILE_CONTENT)
    string(REPLACE "\n" ";" CONTENTS "${FILE_CONTENT}")
    list(REMOVE_ITEM CONTENTS "")
    set(${OUT_CONTENTS} "${CONTENTS}" PARENT_SCOPE)
endfunction()

function (get_compiler_flags COMPILER_VARIANT OUT_FLAGS)
    find_package (Python COMPONENTS Interpreter Development)

    if (NOT PYTHON_FOUND)
        message(FATAL_ERROR "Python not found.")
    endif()

    execute_process(
        COMMAND "${Python_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/{[(PROJ_OR_EMPTY)]}utils/fetch_flags.py" ${COMPILER_VARIANT} ${CMAKE_BUILD_TYPE}
        OUTPUT_VARIABLE TEMP
        ERROR_VARIABLE ERROR_MSG
        RESULT_VARIABLE RESULT
        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}/{[(PROJ_OR_EMPTY)]}utils"
    )

    if (NOT RESULT EQUAL 0)
        message(FATAL_ERROR "Error in fetch_flags.py:\n${ERROR_MSG}")
    endif()

    string(STRIP "${TEMP}" TEMP_CLEAN)
    set(${OUT_FLAGS} ${TEMP_CLEAN} PARENT_SCOPE)
endfunction()

function(install_dy_libs TARGET_NAME OUT_DIR DY_LIBS)
    foreach(DY_LIB ${DY_LIBS})
        add_custom_command(TARGET "${TARGET_NAME}" POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different "${DY_LIB}" "${OUT_DIR}")
    endforeach()
endfunction()

function(add_exec_target TARGET_NAME SOURCE HEADERS INCLUDE_DIRS LINK_LIBS DY_LIBS DEFS FLAGS FEATURES LINKER_FLAGS IS_TEST)
    if (NOT SOURCE)
        return()
    endif()

    if (IS_TEST)
        set(OUT_DIR "${CMAKE_SOURCE_DIR}/{[(BUILD_OR_EMPTY)]}out/test")
    else()
        set(OUT_DIR "${CMAKE_SOURCE_DIR}/{[(BUILD_OR_EMPTY)]}out/bin")
    endif()

    if ("${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
        set(OUT_DIR "${OUT_DIR}/Debug")
    else()
        set(OUT_DIR "${OUT_DIR}/Release")
    endif()

    add_executable("${TARGET_NAME}" ${SOURCE} ${HEADERS})
    target_include_directories("${TARGET_NAME}" PRIVATE ${INCLUDE_DIRS})
    target_link_libraries("${TARGET_NAME}" PRIVATE ${LINK_LIBS})
    target_compile_definitions("${TARGET_NAME}" PRIVATE ${DEFS})
    target_compile_options("${TARGET_NAME}" PRIVATE ${FLAGS})
    target_compile_features("${TARGET_NAME}" PRIVATE ${FEATURES})
    target_link_options("${TARGET_NAME}" PRIVATE ${LINKER_FLAGS})
    set_target_properties("${TARGET_NAME}" PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${OUT_DIR}")
    install_dy_libs("${TARGET_NAME}" "${OUT_DIR}" "${DY_LIBS}")
endfunction()

function(add_lib_target TARGET_NAME SOURCE HEADERS INCLUDE_DIRS LINK_LIBS DY_LIBS DEFS FLAGS FEATURES LINKER_FLAGS IS_SHARED)
    if (NOT SOURCE)
        return()
    endif()

    if ("${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
        set(OUT_DIR "${CMAKE_SOURCE_DIR}/{[(BUILD_OR_EMPTY)]}out/lib/Debug")
    else()
        set(OUT_DIR "${CMAKE_SOURCE_DIR}/{[(BUILD_OR_EMPTY)]}out/lib/Release")
    endif()

    if (IS_SHARED)
        add_library("${TARGET_NAME}" SHARED ${SOURCE} ${HEADERS})
    else()
        add_library("${TARGET_NAME}" STATIC ${SOURCE} ${HEADERS})
    endif()
    
    target_include_directories("${TARGET_NAME}" PUBLIC ${INCLUDE_DIRS})
    target_link_libraries("${TARGET_NAME}" PUBLIC ${LINK_LIBS})
    target_compile_definitions("${TARGET_NAME}" PUBLIC ${DEFS})
    target_compile_options("${TARGET_NAME}" PUBLIC ${FLAGS})
    target_compile_features("${TARGET_NAME}" PUBLIC ${FEATURES})
    target_link_options("${TARGET_NAME}" PUBLIC ${LINKER_FLAGS})
    
    set_target_properties("${TARGET_NAME}" PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${OUT_DIR}"
        LIBRARY_OUTPUT_DIRECTORY "${OUT_DIR}"
        ARCHIVE_OUTPUT_DIRECTORY "${OUT_DIR}")

    install_dy_libs("${TARGET_NAME}" "${OUT_DIR}" "${DY_LIBS}")
endfunction()"""

    proj_or_empty = 'project/' if conf.has_proj_dir else ''
    build_or_empty = 'build/' if conf.is_out_in_build_dir else ''

    functions_cmake = functions_cmake.replace('{[(PROJ_OR_EMPTY)]}', proj_or_empty)
    functions_cmake = functions_cmake.replace('{[(BUILD_OR_EMPTY)]}', build_or_empty)

    utils_dir = gen_dir(cwd, 'utils')
    gen_file(utils_dir, 'functions.cmake', functions_cmake)
    gen_file(utils_dir, 'fetch_flags.py', fetch_flags_py)

def gen_config_dir(cwd: str, conf: ProjectConfig):
    
    c_only_enable = 'true' if conf.use_c else 'false'

    compiler_flags_yaml = f"""# This file was generated by Xen ProjGen.
file: "compiler_flags.yaml"
version: 1.0
author: "XeniaPhe"
license: "MIT License"
github: "https://github.com/XeniaPhe/Xen-ProjGen"
description: "YAML configuration file for compiler flags for GCC, Clang, and MSVC compilers across various build types"

# Basic rules for GCC and CLANG flags
# Enabling warnings: Use -W followed by the warning name (e.g., -Wall).
# Disabling warnings: Use -Wno- followed by the warning name (e.g., -Wno-unused-variable).
# Treat warnings as errors: Use -Werror= followed by the warning name with no spaces in between (e.g., -Werror=return-type)

# Basic rules for MSVC flags
# Enabling warnings: Use /wL followed by the warning number where L is the warning level the warning is enabled at (e.g. /w14061)
# Disable warnings: Use /wd followed by the warning number (e.g. /wd4100)
# Treat warnings as errors: Use /we followed by the warning number (e.g. /we4715)

gcc:
  debug:
    - flag: "-O0"
      description: "Disable optimizations"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html#index-O0"
      enabled: true

    - flag: "-g3"
      description: "Generate debug information"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Debugging-Options.html#index-g"
      enabled: true

    - flag: "-save-temps=obj"
      description: "Save intermediate files to the specified directory (Requires linker flags as well)"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Developer-Options.html#index-save-temps"
      enabled: false

    - flag: "-fverbose-asm"
      description: "Generate verbose assembly code (Requires linker flags as well)"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html#index-fverbose-asm"
      enabled: false

    - flag: "-fsanitize=undefined"
      description: "Enable undefined behavior sanitizer (Requires linker flags as well)"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html#index-fsanitize_003dundefined"
      enabled: false

    - flag: "-fsanitize=address"
      description: "Enable address sanitizer (Requires linker flags as well)"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html#index-fsanitize_003daddress"
      enabled: false

    - flag: "-Wall"
      description: "Enable most warning messages"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wall"
      enabled: true

    - flag: "-Wextra"
      description: "Enable extra warning messages"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wextra"
      enabled: true

    - flag: "-Wconversion"
      description: "Warn about implicit type conversions"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wconversion"
      enabled: true

    - flag: "-Wdouble-promotion"
      description: "Warn if a value is promoted to double"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wdouble-promotion"
      enabled: true

    - flag: "-Wno-unused-parameter"
      description: "Disable warnings about unused parameters"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wno-unused-parameter"
      enabled: true

    - flag: "-Wno-unused-function"
      description: "Disable warnings about unused functions"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wno-unused-function"
      enabled: true

    - flag: "-Wno-unused-result"
      description: "Disable warnings about unused results"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wno-unused-result"
      enabled: true

    - flag: "-Wno-sign-conversion"
      description: "Disable warnings about sign conversion"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wno-sign-conversion"
      enabled: true

    - flag: "-Wfloat-equal"
      description: "Warn about comparisons between floating point values"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wfloat-equal"
      enabled: true

    - flag: "-Wundef"
      description: "Warn if an undefined identifier is evaluated"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wundef"
      enabled: true

    - flag: "-Wshadow"
      description: "Warn when a local variable shadows another variable"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wshadow"
      enabled: true

    - flag: "-Wpointer-arith"
      description: "Warn about pointer arithmetic"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wpointer-arith"
      enabled: true

    - flag: "-Wcast-align"
      description: "Warn when a pointer cast decreases alignment"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wcast-align"
      enabled: true

    - flag: "-Wstrict-prototypes"
      description: "Warn if a function is not declared with a prototype (C only)"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wstrict-prototypes"
      enabled: {c_only_enable}

    - flag: "-Wmissing-prototypes"
      description: "Warn if a function is not declared with a prototype (C only)"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wmissing-prototypes"
      enabled: {c_only_enable}

    - flag: "-Wstrict-overflow=4"
      description: "Warn about optimizations that assume overflow does not occur"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wstrict-overflow"
      enabled: true

    - flag: "-Wwrite-strings"
      description: "Warn when a string literal is assigned to a `char*`"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wwrite-strings"
      enabled: true

    - flag: "-Wcast-qual"
      description: "Warn when a pointer is cast to a different type that may change the type qualifiers"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wcast-qual"
      enabled: true

    - flag: "-Wswitch-default"
      description: "Warn if a `switch` statement does not have a `default` case"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wswitch-default"
      enabled: true

    - flag: "-Wswitch-enum"
      description: "Warn if a `switch` statement does not handle all enumeration values"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wswitch-enum"
      enabled: true

    - flag: "-Werror=return-type"
      description: "Treat missing return statements as errors"
      documentation: "#https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wreturn-type"
      enabled: true

    - flag: "-Werror=implicit-function-declaration"
      description: "Treat implicit function declarations as errors (C only)"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wimplicit-function-declaration"
      enabled: {c_only_enable}

    - flag: "-Werror=incompatible-pointer-types"
      description: "Treat incompatible pointer types as errors (C only)"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wincompatible-pointer-types"
      enabled: {c_only_enable}

    - flag: "-Wformat=2"
      description: "Warn about format string issues"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wformat"
      enabled: true

    - flag: "-Wuninitialized"
      description: "Warn about uninitialized variables"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wuninitialized"
      enabled: true

    - flag: "-Wunreachable-code"
      description: "Warn about code that is unreachable"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc-4.4.7/gcc/Warning-Options.html#index-Wunreachable_002dcode-437"
      enabled: true
  release:
    - flag: "-O3"
      description: "Optimize for maximum performance"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html#index-O3"
      enabled: true

    - flag: "-Ofast"
      description: "Enable -O3 and more optimizations that are not valid for all standard-compliant programs"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html#index-Ofast"
      enabled: false
  minsizerel:
    - flag: "-Os"
      description: "Optimize for size"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html#index-Os"
      enabled: true

    - flag: "-Oz"
      description: "Aggresively optimize for size"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html#index-Oz"
      enabled: false
  relwithdebinfo:
    - flag: "-O2"
      description: "Optimize for speed"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html#index-O2"
      enabled: true

    - flag: "-g3"
      description: "Generate debug information"
      documentation: "https://gcc.gnu.org/onlinedocs/gcc/Debugging-Options.html#index-g"
      enabled: true
clang:
  debug:
    - flag: "-O0"
      description: "Disable optimization"
      documentation: "https://clang.llvm.org/docs/ClangCommandLineReference.html#optimization-level"
      enabled: true

    - flag: "-g3"
      description: "Generate debug information"
      documentation: "https://clang.llvm.org/docs/ClangCommandLineReference.html#debug-level"
      enabled: true

    - flag: "-save-temps=obj"
      description: "Save intermediate files to the output directory (Requires linker flags as well)"
      documentation: "https://clang.llvm.org/docs/ClangCommandLineReference.html#cmdoption-clang-save-temps"
      enabled: false

    - flag: "-fsanitize=undefined"
      description: "Enable undefined behavior sanitizer (Requires linker flags as well)"
      documentation: "https://releases.llvm.org/12.0.0/tools/clang/docs/UndefinedBehaviorSanitizer.html#undefinedbehaviorsanitizer"
      enabled: false

    - flag: "-fsanitize=address"
      description: "Enable address sanitizer (Requires linker flags as well)"
      documentation: "https://releases.llvm.org/12.0.0/tools/clang/docs/AddressSanitizer.html"
      enabled: false

    - flag: "-Wall"
      description: "Enable most warning messages"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wall"
      enabled: true

    - flag: "-Wextra"
      description: "Enable extra warning messages"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wextra"
      enabled: true

    - flag: "-Wconversion"
      description: "Warn about implicit type conversions"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wconversion"
      enabled: true

    - flag: "-Wdouble-promotion"
      description: "Warn if a value is promoted to double"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wdouble-promotion"
      enabled: true

    - flag: "-Wno-unused-parameter"
      description: "Disable warnings about unused parameters"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wunused-parameter"
      enabled: true

    - flag: "-Wno-unused-function"
      description: "Disable warnings about unused functions"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wunused-function"
      enabled: true

    - flag: "-Wno-unused-result"
      description: "Disable warnings about unused results"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wunused-result"
      enabled: true

    - flag: "-Wno-sign-conversion"
      description: "Disable warnings about sign conversion"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wsign-conversion"
      enabled: true

    - flag: "-Wfloat-equal"
      description: "Warn about comparisons between floating point values"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wfloat-equal"
      enabled: true

    - flag: "-Wundef"
      description: "Warn if an undefined identifier is evaluated"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wundef"
      enabled: true

    - flag: "-Wshadow"
      description: "Warn when a local variable shadows another local variable"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wshadow"
      enabled: true

    - flag: "-Wpointer-arith"
      description: "Warn about pointer arithmetic"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wpointer-arith"
      enabled: true

    - flag: "-Wcast-align"
      description: "Warn when a pointer cast decreases alignment"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wcast-align"
      enabled: true

    - flag: "-Wstrict-prototypes"
      description: "Warn if a function is not declared with a prototype (C only)"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wstrict-prototypes"
      enabled: {c_only_enable}

    - flag: "-Wmissing-prototypes"
      description: "Warn if a function is not declared with a prototype (C only)"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wmissing-prototypes"
      enabled: {c_only_enable}

    - flag: "-Wwrite-strings"
      description: "Warn when a string literal is assigned to a `char*`"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wwrite-strings"
      enabled: true

    - flag: "-Wcast-qual"
      description: "Warn when a pointer is cast to a different type that may change the type qualifiers"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wcast-qual"
      enabled: true

    - flag: "-Wswitch-default"
      description: "Warn if a `switch` statement does not have a `default` case"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wswitch-default"
      enabled: true

    - flag: "-Wswitch-enum"
      description: "Warn if a `switch` statement does not handle all enumeration values"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wswitch-enum"
      enabled: true

    - flag: "-Werror=return-type"
      description: "Treat missing return statements as errors"
      documentation: "https://clang.llvm.org/docs/UsersManual.html#cmdoption-Werror #https://clang.llvm.org/docs/DiagnosticsReference.html#wreturn-type"
      enabled: true

    - flag: "-Werror=implicit-function-declaration"
      description: "Treat implicit function declarations as errors (C only)"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wimplicit-function-declaration"
      enabled: {c_only_enable}

    - flag: "-Werror=incompatible-pointer-types"
      description: "Treat incompatible pointer types as  (C only)"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wincompatible-pointer-types"
      enabled: {c_only_enable}

    - flag: "-Wformat=2"
      description: "Warn about format string issues"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wformat"
      enabled: true

    - flag: "-Wuninitialized"
      description: "Warn about uninitialized variables"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wuninitialized"
      enabled: true

    - flag: "-Wunreachable-code-aggressive"
      description: "Warn about aggressive unreachable code detection"
      documentation: "https://clang.llvm.org/docs/DiagnosticsReference.html#wunreachable-code"
      enabled: true
  release:
    - flag: "-O3"
      description: "Optimize for maximum performance"
      documentation: "https://clang.llvm.org/docs/ClangCommandLineReference.html#optimization-level"
      enabled: true

    - flag: "-ffast-math"
      description: "Enable math optimizations such as faster floating point operations that are not valid for all standard-compliant programs"
      documentation: "https://clang.llvm.org/docs/ClangCommandLineReference.html#optimization-level"
      enabled: false
  minsizerel:
    - flag: "-Os"
      description: "Optimize for size"
      documentation: "https://clang.llvm.org/docs/ClangCommandLineReference.html#optimization-level"
      enabled: true

    - flag: "-Oz"
      description: "Aggresively optimize for size"
      documentation: "https://clang.llvm.org/docs/ClangCommandLineReference.html#optimization-level"
      enabled: false
  relwithdebinfo:
    - flag: "-O2"
      description: "Optimize for speed"
      documentation: "https://clang.llvm.org/docs/ClangCommandLineReference.html#optimization-level"
      enabled: true

    - flag: "-g3"
      description: "Generate debug information"
      documentation: "https://clang.llvm.org/docs/ClangCommandLineReference.html#debug-level"
      enabled: true
msvc:
  debug:
    - flag: "/Od"
      description: "Disable optimization"
      documentation: "https://learn.microsoft.com/en-us/cpp/build/reference/od-disable-debug?view=msvc-170"
      enabled: true

    - flag: "/Zi"
      description: "Generate complete debug information"
      documentation: "https://learn.microsoft.com/en-us/cpp/build/reference/z7-zi-zi-debug-information-format?view=msvc-170"
      enabled: true

    - flag: "/FAs /Fa ./out/dump/"
      description: "Generate source and assembly code listings in the specified directory"
      documentation: "https://learn.microsoft.com/en-us/cpp/build/reference/fa-fa-listing-file?view=msvc-170"
      enabled: true

    - flag: "/RTC1"
      description: "Enable run-time error checks"
      documentation: "https://learn.microsoft.com/en-us/cpp/build/reference/rtc-run-time-error-checks?view=msvc-170"
      enabled: true

    - flag: "/fsanitize=address"
      description: "Enable address sanitizer"
      documentation: "https://learn.microsoft.com/en-us/cpp/build/reference/fsanitize?view=msvc-170"
      enabled: true

    - flag: "/W4"
      description: "Set warning level to 4, enable most warning messages"
      documentation: "https://learn.microsoft.com/en-us/cpp/build/reference/compiler-option-warning-level?view=msvc-170"
      enabled: true

    - flag: "/w14244"
      description: "Warn about implicit type conversions (Already included at level 2)"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-levels-3-and-4-c4244?view=msvc-170"
      enabled: true

    - flag: "/wd4100"
      description: "Disable warnings about unused parameters"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-4-c4100?view=msvc-170"
      enabled: true

    - flag: "/wd4505"
      description: "Disable warnings about unused functions"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-4-c4505?view=msvc-170"
      enabled: true

    - flag: "/wd4365"
      description: "Disable warnings about sign conversion (Off by default)"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-4-c4365?view=msvc-170"
      enabled: true

    - flag: "/w14668"
      description: "Warn if an undefined identifier is evaluated"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-4-c4668?view=msvc-170&redirectedfrom=MSDN"
      enabled: true

    - flag: "/w14459"
      description: "Warn when a local variable shadows another variable (Already included at level 4)"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-4-c4459?view=msvc-170"
      enabled: true

    - flag: "/w14061"
      description: "Warn if a `switch` statement does not handle all enumeration values (Off by default)"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-4-c4061?view=msvc-170"
      enabled: true

    - flag: "/w14062"
      description: "Warn if a `switch` statement does not have a `default` case (Off by default)"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-4-c4062?view=msvc-170"
      enabled: true

    - flag: "/we4715"
      description: "Treat missing return statements as errors"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-1-c4715?view=msvc-170"
      enabled: true

    - flag: "/we4013"
      description: "Treat implicit function declarations as errors"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-3-c4013?view=msvc-170"
      enabled: true

    - flag: "/we4133"
      description: "Treat incompatible pointer types as errors"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-3-c4133?view=msvc-170"
      enabled: true

    - flag: "/w14101"
      description: "Warn about uninitialized variables when they're not used (Already included at level 3)"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-3-c4101?view=msvc-170"
      enabled: true

    - flag: "/w14700"
      description: "Warn about uninitialized variables when they're used (Already included at level 1)"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-1-and-level-4-c4700?view=msvc-170"
      enabled: true

    - flag: "/wd4189"
      description: "Disable warnings about initialized but unreferenced variables"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-4-c4189?view=msvc-170"
      enabled: true

    - flag: "/w14702"
      description: "Warn about code that is unreachable (Already included at level 4)"
      documentation: "https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-4-c4702?view=msvc-170"
      enabled: true
  release:
    - flag: "/O2"
      description: "Optimize for maximum speed"
      documentation: "https://learn.microsoft.com/en-us/cpp/build/reference/o1-o2-minimize-size-maximize-speed?view=msvc-170"
      enabled: true

    - flag: "/fp:fast"
      description: "Optimize floating point math for speed and space but the compiler may omit rounding and special values (NaN, infinity) may not behave strictly."
      documentation: "https://learn.microsoft.com/en-us/cpp/build/reference/fp-specify-floating-point-behavior?view=msvc-170#fast"
      enabled: false
  minsizerel:
    - flag: "/O1"
      description: "Optimize for size"
      documentation: "https://learn.microsoft.com/en-us/cpp/build/reference/o1-optimize-for-size?view=msvc-170"
      enabled: true
  relwithdebinfo:
    - flag: "/O1"
      description: "Optimize for size"
      documentation: "https://learn.microsoft.com/en-us/cpp/build/reference/o1-optimize-for-size?view=msvc-170"
      enabled: true

    - flag: "/Zi"
      description: "Generate complete debug information"
      documentation: "https://learn.microsoft.com/en-us/cpp/build/reference/z7-zi-zi-debug-information-format?view=msvc-170"
      enabled: true

    - flag: "/FAs /Fa ./out/dump/"
      description: "Generate source and assembly code listings in the specified directory"
      documentation: "https://learn.microsoft.com/en-us/cpp/build/reference/fa-fa-listing-file?view=msvc-170"
      enabled: true"""

    config_dir = gen_dir(cwd, 'config')
    gen_file(config_dir, 'compiler_flags.yaml', compiler_flags_yaml)
    gen_file(config_dir, 'definitions.txt', '')
    gen_file(config_dir, 'compiler_features.txt')
    gen_file(config_dir, 'linker_flags.txt')

def gen_workspace_file(cwd: str, conf: ProjectConfig):
    if not conf.should_gen_workspace_file:
        return

    workspace_content = """{
    "folders": [
        {
            "name": "{[(PROJ_NAME)]}",
            "path": "{[(PROJ_PATH)]}"
        },{[(INCLUDE_OR_EMPTY)]}
        {[(COMMENT_OR_EMPTY)]}{
        {[(COMMENT_OR_EMPTY)]}    "name": "src",
        {[(COMMENT_OR_EMPTY)]}    "path": "{[(SRC_PATH)]}"
        {[(COMMENT_OR_EMPTY)]}}
    ]
}"""

    proj_path = './..' if conf.has_proj_dir else '.'
    source_root = f'{conf.proj_name}/' if conf.has_proj_name_dir else ''
    src_path = f'{proj_path}/{source_root}src'

    include_or_empty = ''
    if conf.should_gen_include_dir:
        include_path = f'{proj_path}/{source_root}{'src/include' if conf.is_include_dir_inside_src else 'include'}'

        include_or_empty = """
        {[(COMMENT_OR_EMPTY)]}{
        {[(COMMENT_OR_EMPTY)]}    "name": "include",
        {[(COMMENT_OR_EMPTY)]}    "path": "{[(INCLUDE_PATH)]}"
        {[(COMMENT_OR_EMPTY)]}},"""

        include_or_empty = include_or_empty.replace('{[(INCLUDE_PATH)]}', include_path)

    comment_or_empty = '' if conf.should_add_src_and_include_dirs_to_ws else '// '

    workspace_content = workspace_content.replace('{[(PROJ_NAME)]}', conf.proj_name)
    workspace_content = workspace_content.replace('{[(PROJ_PATH)]}', proj_path)
    workspace_content = workspace_content.replace('{[(INCLUDE_OR_EMPTY)]}', include_or_empty)
    workspace_content = workspace_content.replace('{[(COMMENT_OR_EMPTY)]}', comment_or_empty)
    workspace_content = workspace_content.replace('{[(SRC_PATH)]}', src_path)
    gen_file(cwd, f'{conf.proj_name}.code-workspace', workspace_content)
    
def gen_proj_dir(cwd: str, conf: ProjectConfig):
    proj_dir = gen_dir(cwd, 'project') if conf.has_proj_dir else cwd
    gen_config_dir(proj_dir, conf)
    gen_utils_dir(proj_dir, conf)
    gen_workspace_file(proj_dir, conf)

def gen_proj_name_dir(cwd: str, conf: ProjectConfig):
    if conf.use_cpp:
        main_file_name = 'main.cpp'
        main_content = """#include <iostream>

int main() {
    std::cout << "Hello, world!" << std::endl;
    return 0;
}"""
    else:
        main_file_name = 'main.c'
        main_content = """#include <stdio.h>

int main() {
    printf("Hello, world!\\n");
    return 0;
}"""
    
    proj_name_dir = gen_dir(cwd, conf.proj_name) if conf.has_proj_name_dir else cwd
    gen_dir(proj_name_dir, 'libs')
    src_dir = gen_dir(proj_name_dir, 'src')
    gen_file(src_dir, main_file_name, main_content)

    if conf.should_gen_include_dir:
        gen_dir(src_dir if conf.is_include_dir_inside_src else proj_name_dir, 'include')

    if conf.should_include_tests:
        gen_dir(proj_name_dir, 'test')

def gen_docs_dir(cwd: str, conf: ProjectConfig):
    readme_md = r"""<h1 style="text-align: center; color: #ff9400;">Xen CMake C/C++ ProjGen Documentation</h1>

```yaml
file: "readme.md"
version: 1.0
author: "XeniaPhe"
license: "MIT License"
github: "https://github.com/XeniaPhe/Xen-ProjGen"
description: "Documentation"
```
Welcome to the documentation of ***Xen ProjGen***! Xen Projgen is a simple python script that generates simple and highly customizable CMake C/C++ projects with single targets. It is aimed to eliminate the setup step for small and simple projects but it can also be used as a stepping stone for larger projects with more complex needs such as multiple targets, toolchain and preset files, cross-compiling, multi-step building etc. This guide should help you understand how to effectively work with this generated project structure.
### **Table Of Contents**
1. [**`Building The Project`**](building.md)
2. [**`Configuration`**](configuration.md)
3. [**`Linking Libraries`**](libraries.md)

<br>[`<-- Prev Page`](libraries.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Main Page`](readme.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Next Page -->`](building.md)
"""

    building_md = r"""[`<-- Prev Page`](readme.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Main Page`](readme.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Next Page -->`](configuration.md)
<h2 style="text-align: center; color: #ff9400;">Building The Project</h2>

### **Prerequisites**
To be able to build your project, you have to have at least **CMake 3.15**, **Python3** and any one of the **GCC**, **Clang**, and **MSVC** compilers installed and added to the **PATH** on your system.
### **Supported Platforms**
Since the project structure is fully self-contained and does not include any platofrm-specific code or features, it should be platform-agnostic and work across different operating systems, including Windows, Linux and macOS. However, it has only been tested on Windows.
### **1 - Building With CMake Tools**
If you are using Visual Studio Code to develop your project, you can simply install the CMake Tools extension and use its GUI to configure, build and run the project. This really adds it an IDE-like experience where you can focus on developing and leave the rest to the CMake Tools.
### **2 - Building From The Terminal**
Build pipeline of this project is not anything complicated. You can simply configure CMake with the generator and compiler of your choice along with the build type and any other variables you want to set. You can then build it using the *`cmake --build`* command or the build command of the build system you are using. Although building with CMake Tools is easier and quicker, you can gain more control over the build process by using the terminal to build the project. This allows you to make use of toolchain files, preset files, and pass custom or specific flags to CMake, which can be particularly useful for cross-compiling, fine-tuning build configurations, or setting up advanced options not readily accessible through the CMake Tools UI.

[`<-- Prev Page`](readme.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Main Page`](readme.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Next Page -->`](configuration.md)
"""

    configuration_md = r"""[`<-- Prev Page`](building.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Main Page`](readme.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Next Page -->`](libraries.md)
<h2 style="text-align: center; color: #ff9400;">Configuration</h2>

Inside the config directory are four files: **compiler_features.txt**, **compiler_flags.yaml**, **definitions.txt**, **linker_flags.txt** . Using these files, you can configure various aspects of the build system, including [***`setting compiler flags`***](#configuring-compiler-flags), [***`adding preprocessor definitions`***](#adding-preprocessor-definitions), [***`adjusting linker options`***](#configuring-linker-flags), and [***`enabling specific compiler features`***](#configuring-compiler-features). This should allow you to optimize your build for various requirements. However, for any changes made in these files to propagate to your build, you should **reconfigure CMake and rebuild** your project.
### **Configuring Compiler Flags** &nbsp; [`⇧`](#)
Inside the **compiler_flags.yaml** file, you will find various pre-defined configurations organized by compiler and build type. This file serves as a comprehensive collection of the most commonly used and necessary compiler flags across the three major compilers: **GCC**, **Clang**, and **MSVC**. Below is the general structure of the file:
```yaml
gcc:
  debug:
    - LIST OF FLAG ENTRIES
  release:
    - LIST OF FLAG ENTRIES
  minsizerel:
    - LIST OF FLAG ENTRIES
  relwithdebinfo:
    - LIST OF FLAG ENTRIES
clang:
  debug:
.
.
.
```
where each flag entry looks like:
```yaml
- flag: "-Wall" # The flag itself
  description: "Enable most warning messages" # Description for the flag
  documentation: "https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wall" # Link to the documentation page of the flag, if any
  enabled: true # Whether the flag is enabled or not (true or false)
```

You can enable or disable certain flags using the **enabled** field and add your own flags under designated configurations (e.g., *GCC, Debug*). The **description** and **documentation** fields can be **omitted** when adding new flags.

The **compiler_flags.yaml** file is parsed and processed by fetch_flags.py, which retrieves the flags for use in CMake. Since, the script is invoked from within CMake, remember to **reconfigure** your project for any changes made to this file to take effect.
### **Adding Preprocessor Definitions** &nbsp; [`⇧`](#)
You can define new preprocessor directives by adding entries to the **definitions.txt** file, with each entry separated by a new line. While you can assign string literals or numbers to your directives, but note that most compilers do not allow passing function-style preprocessor macros. Here are some examples:
```json
GAME_MODE="DEVELOPMENT"
NR_PLAYERS=1
ENABLE_OPTIMIZATIONS
```
After making changes in **definitions.txt**, remember to **reconfigure** CMake for the new definitions to take effect in your project.

In addition to the custom definitions you add through **definitions.txt**, the CMake script provided in this project automatically defines several preprocessor directives that supply valuable information about the build environment:

* ***Operating System :***
    * **`WINDOWS`**
    * **`LINUX`** (*Also defines ***`UNIX`****)
    * **`MACOS`** (*Also defines ***`UNIX`****)
    * **`UNIX`**
    * **`OTHER_OS`**
* ***Compiler :***
    * **`GCC_COMPILER`**
    * **`CLANG_COMPILER`**
    * **`CLANG_CL_COMPILER`**
    * **`MSVC_COMPILER`**
    * **`UNKNOWN_COMPILER`**
* ***Build Type :***
    * **`DEBUG`**
    * **`RELEASE`**
    * **`MINSIZEREL`**
    * **`RELWITHDEBINFO`**
* ***Word Size :***
    * **`WORD_SIZE_32`**
    * **`WORD_SIZE_64`**
### **Configuring Linker Flags** &nbsp; [`⇧`](#)
You can customize linker behavior by adding entries to the **linker_flags.txt** file. Each entry should be placed on a new line. Linker flags allow you to control various aspects of the linking process, such as specifying additional libraries, setting link options, or defining the output format. Here are some examples of what you might include:
```
-pthread
-nostdlib
-nostdlib++
-static-libasan
-static-libubsan
```
After modifying the **linker_flags.txt** file, ensure that you **reconfigure** CMake to apply the new linker flags to your project.
### **Configuring Compiler Features** &nbsp; [`⇧`](#)
You can specify compiler features by adding entries to the **compiler_features.txt** file. Each feature should be listed on a new line. Here are some examples:
```
cxx_constexpr
cxx_static_assert
cxx_variadic_templates
```
After making changes to **compiler_features.txt**, remember to **reconfigure** CMake for the new settings to take effect in your project.

[`<-- Prev Page`](building.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Main Page`](readme.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Next Page -->`](libraries.md)
"""

    libraries_md = r"""[`<-- Prev Page`](configuration.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Main Page`](readme.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Next Page -->`](readme.md)
<h2 style="text-align: center; color: #ff9400;">Linking Libraries</h2>

### **Linking Through *`libs/`* Directory**
To link libraries through the *`libs/`* directory, simply copy the library folder into *`libs/`* and ensure that the structure of your library follows this format:
```yaml
libs/
├── example_lib/
│   ├── include/
│   └── lib/
└── example_header_only_lib/
    └── include/
```
If the library structure adheres to this format, the provided CMake script will automatically include all the headers found in the *`include/`* directory, link all the static and dynamic import libraries located in the *`lib/`* directory, and copy any dynamic libraries from *`lib/`* into the target output directory upon build.

***`Warning :`*** When adding libraries that contain multiple linking options(e.g., Both dynamic and static library files), be cautious. The provided CMake script will attempt to link **all of them**. In this case, you must manually delete or exclude the unwanted files to avoid linking conflicts.
### **Linking Through CMake Modules and Configs**
Linking through the *`libs/`* directory is not applicable or possible in some situations or for some libraries, such as for system-provided libraries like *`OpenGL`*. In such cases, you should write your own *`Find<Library>.cmake`* modules or find existing ones. In either case, you unfortunately have to modify the provided CMake script and make it work with the rest of the project, since there is no way to automate this process to work with all the libraries.

[`<-- Prev Page`](configuration.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Main Page`](readme.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Next Page -->`](readme.md)
"""

    docs_dir = gen_dir(cwd, 'docs')
    gen_file(docs_dir, 'readme.md', readme_md)
    gen_file(docs_dir, 'building.md', building_md)
    gen_file(docs_dir, 'configuration.md', configuration_md)
    gen_file(docs_dir, 'libraries.md', libraries_md)

def gen_readme_file(cwd: str, conf: ProjectConfig):
    if not conf.should_gen_readme:
        return
    
    gen_file(cwd, 'README.md', f'# {conf.proj_name}')

def gen_cmakelists_file(cwd: str, conf: ProjectConfig):
    cmake_lists = r"""# This file was generated by Xen ProjGen.
# File: CMakeLists.txt
# Version: 1.0
# Author: XeniaPhe
# License: MIT License
# Github: https://github.com/XeniaPhe/Xen-ProjGen
# Description: Configures the build system for the project, defining targets, dependencies and settings

cmake_minimum_required(VERSION 3.15...3.30)
include("{[(FUNCTIONS_CMAKE_PATH)]}")

project({[(PROJ_NAME)]} VERSION 0.1.0 LANGUAGES{[(LANGS)]})
{[(LANGUAGE_STANDARDS)]}
set(TARGET "{[(TARGET_NAME)]}")

# Make a list of useful preprocessor definitions to add to the build
set(DEFS "")
get_compiler_definition(COMPILER_DEFINITION)
get_compiler_variant(${COMPILER_DEFINITION} COMPILER_VARIANT)
list(APPEND DEFS "${COMPILER_DEFINITION}")
append_architectural_definitions(DEFS)
append_os_definitions(DEFS)
append_build_definitions(DEFS)

# Also add the user defined definitions to the list
read_file("{[(CONFIG_PATH)]}definitions.txt" USER_DEFS)
list(APPEND DEFS "${USER_DEFS}")

# Get the compiler flags for the target compiler
get_compiler_flags(${COMPILER_VARIANT} FLAGS)

# Get the compiler features
read_file("{[(CONFIG_PATH)]}compiler_features.txt" FEATURES)

# Get the link options
read_file("{[(CONFIG_PATH)]}linker_flags.txt" LINKER_FLAGS)
{[(SET_SOURCE_DIR_OR_EMPTY)]}
file(GLOB LINK_LIBS {[(LINK_LIBS_WILDCARD)]})
file(GLOB DY_LIBS {[(DY_LIBS_WILDCARD)]})
file(GLOB INCLUDE_DIRS {[(INCLUDE_DIRS_WILDCARD)]})
file(GLOB_RECURSE HEADERS{[(HEADERS_WILDCARD)]})
file(GLOB_RECURSE SOURCE{[(SOURCE_WILDCARD)]}){[(TEST_FILES_COMMAND)]}
{[(ADD_INCLUDE_DIR)]}
{[(ADD_TARGET)]}{[(ADD_TEST)]}"""

    cmake_root = '${CMAKE_SOURCE_DIR}/'
    source_root = cmake_root
    set_source_dir = ''
    if conf.has_proj_name_dir:
        set_source_dir = f'\nset(SOURCE_ROOT "{cmake_root}{conf.proj_name}/")\n'
        source_root = '${SOURCE_ROOT}/'

    lib_wc = 'libs/*/'
    libs_wc = f'{lib_wc}lib/*'
    link_libs_wildcard = f'"{source_root}{libs_wc}.a" "{source_root}{libs_wc}.lib"'
    dy_libs_wildcard = f'"{source_root}{libs_wc}.so" "{source_root}{libs_wc}.dll" "{source_root}{libs_wc}.dylib"'
    include_dirs_wildcard = f'"{source_root}{lib_wc}include"'

    proj_root = f'{cmake_root}project/' if conf.has_proj_dir else cmake_root
    functions_cmake_path = f'{proj_root}utils/functions.cmake'
    config_path = f'{proj_root}config/'

    if conf.should_gen_include_dir:
        include_path_from_source_root = 'src/include' if conf.is_include_dir_inside_src else 'include'
        add_include_dir =  f'\nlist(APPEND INCLUDE_DIRS "{source_root}{include_path_from_source_root}")\n'
    else:
        include_path_from_source_root = 'src'
        add_include_dir = ''

    languages = ''
    language_standards = ''
    headers_wildcard = ''
    source_wildcard = ''
    test_files_command = '\nfile(GLOB_RECURSE TESTS'

    if not conf.use_c and conf.should_list_h_files:
        headers_wildcard += f' "{source_root}{include_path_from_source_root}/*.h"'

    if conf.use_c:
        languages += ' C'
        language_standards += f"""set(CMAKE_C_STANDARD {conf.c_std})
set(CMAKE_C_STANDARD_REQUIRED ON)
"""     
        headers_wildcard += f' "{source_root}{include_path_from_source_root}/*.h"'      
        source_wildcard += f' "{source_root}src/*.c"'
        test_files_command += f' "{source_root}test/*.c"'
    if conf.use_cpp:
        languages += ' CXX'
        language_standards += f"""set(CMAKE_CXX_STANDARD {conf.cpp_std})
set(CMAKE_CXX_STANDARD_REQUIRED ON)
"""
        headers_wildcard += f' "{source_root}{include_path_from_source_root}/*.hpp"'      
        source_wildcard += f' "{source_root}src/*.cpp"'
        test_files_command += f' "{source_root}test/*.cpp"'
        
    test_files_command = (test_files_command + ')') if conf.should_include_tests else ''

    target_and_source = '"${TARGET}" "${SOURCE}"'
    common_params = '"${HEADERS}" "${INCLUDE_DIRS}" "${LINK_LIBS}" "${DY_LIBS}" "${DEFS}" "${FLAGS}" "${FEATURES}" "${LINKER_FLAGS}"'
    if target_type == 'Executable':
        add_target = f'add_exec_target({target_and_source} {common_params} FALSE)'
    elif target_type == 'Dynamic Library':
        add_target = f'add_lib_target({target_and_source} {common_params} TRUE)'
    else:
        add_target = f'add_lib_target({target_and_source} {common_params} FALSE)'

    if conf.should_include_tests:
        add_test = """
add_exec_target("tests" "${TESTS}" """ + f'{common_params}' """ TRUE)

enable_testing()
add_test(NAME "tests" COMMAND "tests")"""
    else:
        add_test = ''

    cmake_lists = cmake_lists.replace('{[(FUNCTIONS_CMAKE_PATH)]}', functions_cmake_path)
    cmake_lists = cmake_lists.replace('{[(PROJ_NAME)]}', conf.proj_name)
    cmake_lists = cmake_lists.replace('{[(LANGS)]}', languages)
    cmake_lists = cmake_lists.replace('{[(LANGUAGE_STANDARDS)]}', language_standards)
    cmake_lists = cmake_lists.replace('{[(TARGET_NAME)]}', conf.target_name)
    cmake_lists = cmake_lists.replace('{[(CONFIG_PATH)]}', config_path)
    cmake_lists = cmake_lists.replace('{[(SET_SOURCE_DIR_OR_EMPTY)]}', set_source_dir)
    cmake_lists = cmake_lists.replace('{[(LINK_LIBS_WILDCARD)]}', link_libs_wildcard)
    cmake_lists = cmake_lists.replace('{[(DY_LIBS_WILDCARD)]}', dy_libs_wildcard)
    cmake_lists = cmake_lists.replace('{[(INCLUDE_DIRS_WILDCARD)]}', include_dirs_wildcard)
    cmake_lists = cmake_lists.replace('{[(HEADERS_WILDCARD)]}', headers_wildcard)
    cmake_lists = cmake_lists.replace('{[(SOURCE_WILDCARD)]}', source_wildcard)
    cmake_lists = cmake_lists.replace('{[(TEST_FILES_COMMAND)]}', test_files_command)
    cmake_lists = cmake_lists.replace('{[(ADD_INCLUDE_DIR)]}', add_include_dir)
    cmake_lists = cmake_lists.replace('{[(ADD_TARGET)]}', add_target)
    cmake_lists = cmake_lists.replace('{[(ADD_TEST)]}', add_test)

    gen_file(cwd, 'CMakeLists.txt', cmake_lists)

def setup_git(cwd: str, conf: ProjectConfig):
    if not conf.should_init_git:
        return
    
    proj_name_dir_or_empty = f'{conf.proj_name}/' if conf.has_proj_name_dir else ''

    gitignore = f"""# This file was generated by Xen ProjGen.
# File: .gitignore
# Version: 1.0
# Author: XeniaPhe
# License: MIT License
# Github: https://github.com/XeniaPhe/Xen-ProjGen
# Description: Tells git which extensions and files to ignore when pushing to remote repository
    
# Ignore build artifacts
/build/
build/
*.ninja
*.ninja_deps
*.ninja_log
CMakeFiles
CMakeCache.txt
cmake_install.cmake
Makefile
CMakeScripts
CMakeLists.txt.user
Testing
install_manifest.txt
compile_commands.json
CTestTestfile.cmake
_deps
CMakeUserPresets.json

#Ignore generated docs files
docs/readme.md
docs/building.md
docs/configuration.md
docs/libraries.md

# Ignore binary and object files
*.o
*.obj
*.a
*.so
*.dll
*.dylib
*.lib
*.exe
*.out
*.app
*.pdb
*.idb
*.d
*.gcno
*.gcda
*.gcov

# Do not ignore dependencies
!{proj_name_dir_or_empty}libs/*/lib/*.a
!{proj_name_dir_or_empty}libs/*/lib/*.so
!{proj_name_dir_or_empty}libs/*/lib/*.lib
!{proj_name_dir_or_empty}libs/*/lib/*.dll
!{proj_name_dir_or_empty}libs/*/lib/*.dylib

# Ignore IDE-specific files and directories
.vscode/
*.code-workspace

# Ignore temporary files and directories
*.tmp
*.swp
*.swo
*.sublime-workspace
*.sublime-project
*.DS_Store
*.gdb_history
*.clangd/
*.vscode/
*.vscode-test/
*.gtest/

# Ignore generated files from IDEs or build systems
*.log

# Ignore files generated by various tools
*.dSYM/
*.pyo
*.pyc
*.pyd
*.class

# Ignore Python virtual environments (if applicable)
venv/
ENV/
env/"""
    
    gen_file(cwd, '.gitignore', gitignore)
    subprocess.run(['git', 'init'], cwd = cwd)

    if conf.should_commit_git:
        subprocess.run(['git', 'add', '.'], cwd = cwd)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=cwd)

def preview_proj(conf: ProjectConfig):    
    print('\nProject Preview:\n')

    print(f'  -- Project Name       :    {conf.proj_name}')
    print(f'  -- VS Code Project    :    {'Yes' if conf.should_gen_vscode_files else 'No'}')
    print(f'  -- Target Name        :    {conf.target_name}')
    print(f'  -- Target Type        :    {conf.target_type}')

    plural = ' '
    if conf.use_c:
        if conf.c_std == '89' or conf.c_std == '90':
            langs = 'C89/C90'
        else:
            langs = f'C{conf.c_std}'

        if conf.use_cpp:
            langs += f' & C++{conf.cpp_std}'
            plural = 's'
    else:
        langs = f'C++{conf.cpp_std}'
    
    print(f'  -- Language{plural}          :    {langs}')

    if not conf.use_c:
        print(f'  ---- List .h files    :    {'Yes' if conf.should_list_h_files else 'No'}')

    print(f'  -- Testing            :    {'Enabled' if conf.should_include_tests else 'Disabled'}')

    if not conf.should_init_git:
        git = 'Not Initialize'
    elif not conf.should_commit_git:
        git = 'Initialize'
    else:
        git = 'Initialize & Commit'

    print(f'  -- git                :    {git}')

    space =  '    '
    branch = '├── '
    line =   '│   '
    leaf =   '└── '

    print(f'\n{conf.proj_name}/')

    if conf.should_init_git:
        print(branch + '.git/')

    if conf.should_gen_vscode_files:
        print(branch + '.vscode/')
        print(line + branch + 'launch.json')
        print(line + branch + 'settings.json')
        print(line + leaf + 'tasks.json')
    
    print(branch + 'build/')

    if conf.is_out_in_build_dir:
        print(line + leaf + 'out/')
        print(line + space + branch + 'bin/')
        print(line + space + line + branch + 'Debug/')
        print(line + space + line + leaf + 'Release/')
        
        if conf.should_include_tests:
            print(line + space + branch + 'lib/')
            print(line + space + line + branch + 'Debug/')
            print(line + space + line + leaf + 'Release/')
            print(line + space + leaf + 'test/')
            print(line + space + space + branch + 'Debug/')
            print(line + space + space + leaf + 'Release/')
        else:
            print(line + space + leaf + 'lib/')
            print(line + space + space + branch + 'Debug/')
            print(line + space + space + leaf + 'Release/')
    else:
        print(branch + 'out/')
        print(line + branch + 'bin/')
        print(line + line + branch + 'Debug/')
        print(line + line + leaf + 'Release/')

        if conf.should_include_tests:
            print(line + branch + 'lib/')
            print(line + line + branch + 'Debug/')
            print(line + line + leaf + 'Release/')
            print(line + leaf + 'test/')
            print(line + space + branch + 'Debug/')
            print(line + space + leaf + 'Release/')
        else:
            print(line + leaf + 'lib/')
            print(line + space + branch + 'Debug/')
            print(line + space + leaf + 'Release/')

    if conf.has_proj_dir:
        print(branch + 'project/')
        print(line + branch + 'config/')
        print(line + line + branch + 'compiler_features.txt')
        print(line + line + branch + 'compiler_flags.yaml')
        print(line + line + branch + 'definitions.txt')
        print(line + line + leaf + 'linker_flags.txt')

        if conf.should_gen_workspace_file:
            print(line + branch + 'utils/')
        else:
            print(line + leaf + 'utils/')

        if conf.should_gen_workspace_file:
            print(line + line + branch + 'fetch_flags.py')
            print(line + line + leaf + 'functions.cmake')
            print(line + leaf + f'{conf.proj_name}.code-workspace')
        else:
            print(line + space + branch + 'fetch_flags.py')
            print(line + space + leaf + 'functions.cmake')
    else:
        print(branch + 'config/')
        print(line + branch + 'compiler_features.tct')
        print(line + branch + 'compiler_flags.yaml')
        print(line + branch + 'definitions.txt')
        print(line + leaf + 'linker_flags.txt')
        print(branch + 'utils/')
        print(line + branch + 'fetch_flags.py')
        print(line + leaf + 'functions.cmake')

    if conf.has_proj_name_dir:
        print(branch + f'{conf.proj_name}/')
        print(line + branch + 'libs/')

        if not conf.should_include_tests and (not conf.should_gen_include_dir or conf.is_include_dir_inside_src):
            print(line + leaf + 'src/')
        else:
            print(line + branch + 'src/')
        
        if conf.is_include_dir_inside_src:
            if conf.should_include_tests:
                print(line + line + branch + 'include/')
            else:
                print(line + space + branch + 'include/')
        
        if conf.should_include_tests or (conf.should_gen_include_dir and not conf.is_include_dir_inside_src):
            if conf.use_cpp:
                print(line + line + leaf + 'main.cpp')
            else:
                print(line + line + leaf + 'main.c')
        else:
            if conf.use_cpp:
                print(line + space + leaf + 'main.cpp')
            else:
                print(line + space + leaf + 'main.c')

        if conf.should_gen_include_dir and not conf.is_include_dir_inside_src:
            if conf.should_include_tests:
                print(line + branch + 'include/')
            else:
                print(line + leaf + 'include/')
        
        if conf.should_include_tests:
            print(line + leaf + 'test/')
    else:
        print(branch + 'libs/')
        print(branch + 'src/')

        if conf.is_include_dir_inside_src:
            print(line + branch + 'include/')
        
        if conf.use_cpp:
            print(line + leaf + 'main.cpp')
        else:
            print(line + leaf + 'main.c')
        
        if conf.should_gen_include_dir and not conf.is_include_dir_inside_src:
            print(branch + 'include/')
        
        if conf.should_include_tests:
            print(branch + 'test/')
    
    print(branch + 'docs/')
    print(line + branch + 'readme.md')
    print(line + branch + 'building.md')
    print(line + branch + 'configuration.md')
    print(line + leaf + 'libraries.md')

    if conf.should_init_git:
        print(branch + '.gitignore')

    if (conf.has_proj_dir or not conf.should_gen_workspace_file) and not conf.should_gen_readme:
        print(leaf + 'CMakeLists.txt')
    elif (conf.has_proj_dir or not conf.should_gen_workspace_file) and conf.should_gen_readme:
        print(branch + 'CMakeLists.txt')
        print(leaf + 'README.md')
    elif (not conf.has_proj_dir and conf.should_gen_workspace_file) and not conf.should_gen_readme:
        print(branch + 'CMakeLists.txt')
        print(leaf + f'{conf.proj_name}.code-workspace')
    else:
        print(branch + 'CMakeLists.txt')
        print(branch + 'README.md')
        print(leaf + f'{conf.proj_name}.code-workspace')

title_art = r"""
    __   __             _____       __  _____             ______          _ _____            
    \ \ / /            /  __ \     / / /  __ \ _     _    | ___ \        (_)  __ \           
     \ V /  ___ _ __   | /  \/    / /  | /  \/| |_ _| |_  | |_/ / __ ___  _| |  \/ ___ _ __  
     /   \ / _ \ '_ \  | |       / /   | |  |_   _|_   _| |  __/ '__/ _ \| | | __ / _ \ '_ \ 
    / /^\ \  __/ | | | | \__/\  / /    | \__/\|_|   |_|   | |  | | | (_) | | |_\ \  __/ | | |
    \/   \/\___|_| |_|  \____/ /_/      \____/            \_|  |_|  \___/| |\____/\___|_| |_|
                                                                        _/ |                 
                                                                       |__/                  
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                ║
║  Version: 1.0                                                                                  ║
║  Author: XeniaPhe                                                                              ║
║  License: MIT License                                                                          ║
║  Github: https://github.com/XeniaPhe/Xen-ProjGen                                               ║
║  Description: Generates a C/C++ project with a pre-configured CMake setup for a single target  ║
║                                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝"""
print(title_art)

bool_response = yes_or_no(f'Generate a project under {os.getcwd()}')
if not bool_response:
    sys.exit(2)

proj_name = sanitize_file_name(get_input('Project name: '))
target_name_is_proj_name = yes_or_no('Target name matches project name')

if target_name_is_proj_name:
    target_name = proj_name
else:
    target_name = sanitize_file_name(get_input('Target name: '), True)

target_type = choose_one_of('Target type', ['Executable', 'Dynamic Library', 'Static Library'])

use_c = yes_or_no('Include C')

c_std = ""
cpp_std = ""

if use_c:
    c_std = choose_one_of('C Standard', ['C89', 'C90', 'C99', 'C11', 'C17', 'C23'])[1:]

    if c_std == '89':
        c_std = '90'

    use_cpp = yes_or_no('Include C++')
else:
    message('Setting the language to C++')
    use_cpp = True

if use_cpp:
    cpp_std = choose_one_of('C++ Standard', ['C++98', 'C++11', 'C++14', 'C++17', 'C++20', 'C++23', 'C++26'])[3:]

should_list_h_files = use_c

if use_cpp and not use_c:
  should_list_h_files = yes_or_no('Allow listing of .h header files')

should_gen_include_dir = yes_or_no('Add separate include directory')
is_include_dir_inside_src = False

if should_gen_include_dir:
    is_include_dir_inside_src = yes_or_no('Place include directory inside src')

    if not is_include_dir_inside_src:
        message('Placing the include directory at the same level as src')

should_include_tests = yes_or_no('Include testing')

mention_include = should_gen_include_dir and not is_include_dir_inside_src
if mention_include and should_include_tests:
    temp_1 = ''
    temp_2 = ", 'include', and 'test'"
elif mention_include and not should_include_tests:
    temp_1 = ''
    temp_2 = ", and 'include'"
elif not mention_include and should_include_tests:
    temp_1 = ''
    temp_2 = ", and 'test'"
else:
    temp_1 = ' and'
    temp_2 = ''

has_proj_name_dir = yes_or_no(f"Group 'libs',{temp_1} 'src'{temp_2} directories under a '{proj_name}' directory")

should_gen_vscode_files = yes_or_no('Generate Visual Studio Code files')

should_gen_workspace_file = False
should_add_src_and_include_dirs_to_ws = False

if should_gen_vscode_files:
    should_gen_workspace_file = yes_or_no('Generate workspace file')
    if should_gen_workspace_file:
        temp_1 = "and 'include' directories" if should_gen_include_dir else "directory"
        temp_2 = 'these directories' if should_gen_include_dir else 'the source directory'

        should_add_src_and_include_dirs_to_ws = yes_or_no(f"Add 'src' {temp_1} to workspace (Warning: This could clutter the File "
                                             "Explorer and CMake Tools windows, you could also accidentally generate build "
                                             f"files under {temp_2} through CMake Tools)")

has_proj_dir = yes_or_no("Group 'config' and 'utils' directories"
                          f"{" along with the workspace file " if gen_workspace_file else " "}"
                          "under a 'project' directory")

is_out_in_build_dir = yes_or_no("Place the output directory ('out') inside the 'build' directory")

should_gen_readme = yes_or_no('Add README.md')

should_init_git = yes_or_no('Initialize git')
should_commit_git = False

if should_init_git:
    should_commit_git = yes_or_no('Make initial commit')

conf = ProjectConfig(
    proj_name,
    target_name,
    target_type,
    use_c,
    c_std,
    use_cpp,
    cpp_std,
    should_list_h_files,
    should_gen_include_dir,
    is_include_dir_inside_src,
    should_include_tests,
    has_proj_name_dir,
    should_gen_vscode_files,
    should_gen_workspace_file,
    should_add_src_and_include_dirs_to_ws,
    has_proj_dir,
    is_out_in_build_dir,
    should_gen_readme,
    should_init_git,
    should_commit_git)

preview_proj(conf)

print('')
bool_response = yes_or_no('Confirm project')
if not bool_response:
    sys.exit(3)

root_dir = gen_dir(os.getcwd(), conf.proj_name)
gen_vscode_dir(root_dir, conf)
gen_build_dir(root_dir, conf)
gen_proj_dir(root_dir, conf)
gen_proj_name_dir(root_dir, conf)
gen_docs_dir(root_dir, conf)
gen_cmakelists_file(root_dir, conf)
gen_readme_file(root_dir, conf)
setup_git(root_dir, conf)

print('')
message('Project Successfully Generated!')