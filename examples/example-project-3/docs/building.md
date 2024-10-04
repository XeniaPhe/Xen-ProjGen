[`<-- Prev Page`](readme.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
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
