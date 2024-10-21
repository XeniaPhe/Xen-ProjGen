[`<-- Prev Page`](building.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Main Page`](readme.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[`Next Page -->`](libraries.md)
<h2 style="text-align: center; color: #ff9400;">Configuration</h2>

Inside the config directory are four files: **compiler_features.txt**, **compiler_flags.yaml**, **definitions.txt**, **linker_flags.txt** . Using these files, you can configure various aspects of the build system, including [***`setting compiler flags`***](#configuring-compiler-flags), [***`adding preprocessor definitions`***](#adding-preprocessor-definitions), [***`adjusting linker options`***](#configuring-linker-flags), and [***`enabling specific compiler features`***](#configuring-compiler-features). This should allow you to optimize your build for various requirements. However, for any changes made in these files to propagate to your build, you should **reconfigure CMake and rebuild** your project.
### **`Configuring Compiler Flags`**
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
### **`Adding Preprocessor Definitions`**
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
### **`Configuring Linker Flags`**
You can customize linker behavior by adding entries to the **linker_flags.txt** file. Each entry should be placed on a new line. Linker flags allow you to control various aspects of the linking process, such as specifying additional libraries, setting link options, or defining the output format. Here are some examples of what you might include:
```
-pthread
-nostdlib
-nostdlib++
-static-libasan
-static-libubsan
```
After modifying the **linker_flags.txt** file, ensure that you **reconfigure** CMake to apply the new linker flags to your project.
### **`Configuring Compiler Features`**
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
