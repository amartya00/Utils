#CMakeLists.txt

cmake_minimum_required(VERSION 3.0)

# Set up the project
project(UtilsApp)

set(SRC "${CMAKE_CURRENT_SOURCE_DIR}")
set(DEST "${CMAKE_CURRENT_BINARY_DIR}/UtilsApp")

add_custom_target(build
    COMMAND ${CMAKE_COMMAND} -P "${SRC}/CopySrc.cmake" "${SRC}/bin" "${DEST}/bin" "EXEC"
    COMMAND ${CMAKE_COMMAND} -P "${SRC}/CopySrc.cmake" "${SRC}/libs" "${DEST}/libs" "NOEXEC"
    COMMAND ${CMAKE_COMMAND} -P "${SRC}/CopySrc.cmake" "${SRC}/autocompletes" "${DEST}/autocompletes" "NOEXEC")
