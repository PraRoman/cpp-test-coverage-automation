cmake_minimum_required(VERSION 3.16)
project(test_of_script LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Включаем покрытие через опцию ENABLE_COVERAGE
option(ENABLE_COVERAGE "Enable code coverage (GCC)" OFF)

if(ENABLE_COVERAGE AND CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -O0 -g --coverage")
    set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -O0 -g --coverage")
    set(CMAKE_EXE_LINKER_FLAGS_DEBUG "${CMAKE_EXE_LINKER_FLAGS_DEBUG} --coverage")
    set(CMAKE_SHARED_LINKER_FLAGS_DEBUG "${CMAKE_SHARED_LINKER_FLAGS_DEBUG} --coverage")
endif()

add_library(math STATIC src/math.cpp)
target_include_directories(math PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)

find_package(GTest REQUIRED)
find_package(Threads REQUIRED)

enable_testing()

# Тест 1
add_executable(math_tests_func tests/test_func.cpp)
target_include_directories(math_tests_func PRIVATE ${GTEST_INCLUDE_DIRS})
target_link_libraries(math_tests_func
    PRIVATE
    math
    ${GTEST_LIBRARIES}
    Threads::Threads)

# Тест 2
add_executable(math_tests_class 
    tests/test_class.cpp
    src/math_class.cpp
)
target_include_directories(math_tests_class PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src ${GTEST_INCLUDE_DIRS})
target_link_libraries(math_tests_class
    PRIVATE 
    math 
    ${GTEST_LIBRARIES}
    Threads::Threads)

include(GoogleTest)
gtest_discover_tests(math_tests_func)
gtest_discover_tests(math_tests_class)
