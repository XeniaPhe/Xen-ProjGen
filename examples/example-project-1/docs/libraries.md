[`<-- Prev Page`](configuration.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
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
