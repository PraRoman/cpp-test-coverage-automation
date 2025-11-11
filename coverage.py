#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
from pathlib import Path
import shutil
import argparse
import re

#вывод информации
def log(msg): 
    print(f"\033[1;34m[INFO]\033[0m {msg}")

#вывод ошибки
def err(msg):
    print(f"\033[1;31m[ERR]\033 {msg}", file=sys.stderr)
    sys.exit(1)

def warn(msg): print(f"\033[1;33m[WARN]\033[0m {msg}")

#выполнение команды терминала 
def run(cmd, cwd=None, check=True, capture=False):
    log("$ " + " ".join(cmd) + (f"   # cwd={cwd}" if cwd else ""))
    if capture:
        cp = subprocess.run(cmd, cwd=cwd, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if check and cp.returncode != 0:
            err(cp.stdout)
        return cp
    else:
        rc = subprocess.run(cmd, cwd=cwd).returncode
        if check and rc != 0:
            sys.exit(rc)
        return rc

def have(cmd): 
    return shutil.which(cmd) is not None

#Работа с CMakeLists.txt

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def has_enable_testing(txt: str) -> bool:
    return re.search(r'^\s*enable_testing\s*\(\s*\)s*$', txt, re.MULTILINE) is not None

def has_add_test(txt: str) -> bool:
    return re.search(r'^\s*add_test\s*\(', txt, re.MULTILINE) is not None

def has_coverage_option(txt: str) -> bool:
    return re.search(r'option\s*\(\s*ENABLE_COVERAGE\b', txt) is not None

def has_coverage_flags(txt: str) -> bool:
    return "--coverage" in txt and "-O0" in txt and "-g" in txt

def advise_missing_bits(cmake_path: Path):
    txt = read_text(cmake_path)
    tips = []
    if not has_enable_testing(txt):
        tips.append("Добавьте в CMakeLists.txt:  enable_testing()")
    if not has_add_test(txt):
        tips.append("Зарегистрируйте тесты в CTest, например:\n"
                    "  add_test(NAME MyTests\nCOMMAND <ваш_тестовый_бинарник_или_скрипт>)")
    if not has_coverage_option(txt) or not has_coverage_flags(txt):
        tips.append("Добавьте поддержку покрытия (для GCC), например:\n"
                    "  option(ENABLE_COVERAGE \"Enable code coverage (GCC)\" OFF)\n"
                    "  if(ENABLE_COVERAGE AND CMAKE_CXX_COMPILER_ID STREQUAL \"GNU\")\n"
                    "    set(CMAKE_CXX_FLAGS_DEBUG \"${CMAKE_CXX_FLAGS_DEBUG} -O0 -g --coverage\")\n"
                    "    set(CMAKE_EXE_LINKER_FLAGS_DEBUG \"${CMAKE_EXE_LINKER_FLAGS_DEBUG} --coverage\")\n"
                    "    set(CMAKE_SHARED_LINKER_FLAGS_DEBUG \"${CMAKE_SHARED_LINKER_FLAGS_DEBUG} --coverage\")\n"
                    "  endif()")
    return tips

#Установка зависимостей

def apt_install_if_missing(pkg):
    try:
        subprocess.run(["dpkg", "-s", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return
    except Exception:
        pass
    log(f"Устанавливаю пакет: {pkg} (потребуется sudo)")
    run(["sudo", "apt-get", "update", "-qq"])
    run(["sudo", "apt-get", "install", "-y", pkg])

def prepare_deps(allow_install=True):
    need = ["cmake", "g++", "make", "lcov"]
    missing = [x for x in need if not have(x)]
    if not missing:
        return
    if not allow_install:
        err("Не хватает утилит: " + ", ".join(missing) +
            ". Установите вручную (apt-get install cmake g++ make lcov) "
            "или запустите без --no-install.")
    if have("apt-get"):
        for pkg in missing:
            apt_install_if_missing(pkg)
    else:
        err("apt-get не найден. Установите зависимости вручную: " + ", ".join(missing))

#Функции для сборки, тестов и покрытия

def configure(project_dir: Path, build_dir: Path, build_type: str, enable_coverage: bool):
    build_dir.mkdir(parents=True, exist_ok=True)

    base = ["cmake", "-S", str(project_dir), "-B", str(build_dir), f"-DCMAKE_BUILD_TYPE={build_type}"]

    if not enable_coverage:
        run(base)
        return

    cmake_txt = (project_dir / "CMakeLists.txt").read_text(encoding="utf-8")
    has_opt = ("option(" in cmake_txt) and ("ENABLE_COVERAGE" in cmake_txt)

    if has_opt:
        run(base + ["-DENABLE_COVERAGE=ON"])
    else:
        run(base + [
            "-DCMAKE_CXX_FLAGS_DEBUG=-O0 -g --coverage",
            "-DCMAKE_C_FLAGS_DEBUG=-O0 -g --coverage",
            "-DCMAKE_EXE_LINKER_FLAGS_DEBUG=--coverage",
            "-DCMAKE_SHARED_LINKER_FLAGS_DEBUG=--coverage",
        ])

def build(build_dir: Path, jobs: int):
    run(["cmake", "--build", str(build_dir), "-j", str(jobs)])

def ctest_list(build_dir: Path) -> int:
    cp = run(["ctest", "-N"], cwd=str(build_dir), check=False, capture=True)
    print(cp.stdout)
    m = re.search(r"Total Tests:\s*(\d+)", cp.stdout)
    return int(m.group(1)) if m else 0

def run_ctest(build_dir: Path) -> bool:
    total = ctest_list(build_dir)
    if total == 0:
        warn("CTest не обнаружил ни одного теста. Отчёт покрытия будет пустым.")
        return False
    rc = run(["ctest", "--output-on-failure"], cwd=str(build_dir), check=False)
    return rc == 0

def collect_coverage(build_dir: Path, remove_masks):
    run(["lcov", "--directory", ".", "--capture", "--output-file", "coverage.info"], cwd=str(build_dir))
    for m in remove_masks:
        run(["lcov", "--remove", "coverage.info", m, "--output-file", "coverage.info"], cwd=str(build_dir))
    out_dir = build_dir / "coverage_html"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    run(["genhtml", "coverage.info", "--output-directory", "coverage_html"], cwd=str(build_dir))
    return out_dir / "index.html"

def open_report(index_html: Path):
    if have("xdg-open"):
        subprocess.Popen(["xdg-open", str(index_html)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        warn(f"xdg-open не найден. Откройте отчёт вручную: {index_html}")

#Запуск через make (используется, если нет CMakeLists)

def build_with_make(project_dir):
    makefile_path = project_dir / "Makefile"
    content = makefile_path.read_text()

    if "--coverage" not in content:
        err("В makefile нет флагов покрытия (--coverage). Добавьте их.")
    
    rc = run(["make"], cwd=str(project_dir))
    if rc !=0 :
        err("Ошибка при выполнении make")
    
    test_rc = subprocess.run(["make", "test"], cwd  =str(project_dir)).returncode
    
    run(["lcov",
         "--directory", str(project_dir),
         "--capture",
         "--output-file", "coverage.info",
    ], cwd=str(project_dir))

    log("Генерация HTML-отчёта")
    html_dir = project_dir / "coverage.html"
    if html_dir.exists():
        shutil.rmtree(html_dir)

    run([
        "genhtml",
        "coverage.info",
        "--output-directory",
        "coverage_html",
    ], cwd = str(project_dir))
    
    html_dir = project_dir / "coverage_html"
    index_html = html_dir / "index.html"
    log(f"Отчёт покрытия: {index_html}")

    if index_html.exists():
        open_report(index_html)
    else: warn("Файл отчёта не найден")
    cleanup_coverage_files(project_dir)

def cleanup_coverage_files(project_dir: Path):
    log("Удаление временных файлов покрытия")
    patterns = ["*.gcda", "*.gcno", "coverage.info"]
    for pattern in patterns:
        for file in project_dir.glob(pattern):
            try:
                file.unlink()
            except Exception as fails:
                warn(f"Не получилось удалить временные файлы {file}: {fails}")

def main():
    ap = argparse.ArgumentParser(description="Сборка с покрытием, CTest и HTML-отчёт")
    ap.add_argument("--build-with-make", action = "store_true", help = "Игнорировать CMakeLists.txt и собрать через Makefile")
    ap.add_argument("--project-dir", default=".", help="Корень проекта (где CMakeLists.txt)")
    ap.add_argument("--build-dir", default="./build", help="Каталог сборки")
    ap.add_argument("--build-type", default="Debug", choices=["Debug", "Release"])
    ap.add_argument("--no-install", action="store_true", help="Не устанавливать зависимости через apt-get")
    ap.add_argument("--no-clean", action="store_true", help="Не удалять каталог сборки перед конфигурацией")
    ap.add_argument("--no-open", action="store_true", help="Не открывать HTML-отчёт в браузере")
    ap.add_argument("--no-coverage", action="store_true", help="Не включать покрытие (просто прогнать тесты)")
    ap.add_argument("--jobs", "-j", type=int, default=max(os.cpu_count() or 2, 2), help="Параллельных задач сборки")
    ap.add_argument("--remove", action="append", default=["/usr/*", "*/tests/*", "*/CMakeFiles/*"],
                    help="Шаблоны путей для исключения из отчёта (можно указывать несколько раз)")
    ap.add_argument("--fix-cmake", action="store_true",
                    help="Автодобавить недостающие строки в CMakeLists.txt (создаст бэкап *.txt.bak)")
    ap.add_argument("--test-target", default="MyTests",
                    help="Имя тестовой цели для подсказок в автодобавлении")


    args = ap.parse_args()

    project_dir = Path(args.project_dir).resolve()
    build_dir = Path(args.build_dir).resolve()
    cmake_file = project_dir / "CMakeLists.txt"
    make_upper = project_dir / "Makefile"
    make_lower = project_dir / "makefile"
    has_make = make_upper.exists() or make_lower.exists()

    #Зависимости
    prepare_deps(allow_install=not args.no_install)

    if args.build_with_make:
        if not has_make:
            err("Makefile не найден.")
        log("Идёт сборка через Makefile")
        build_with_make(project_dir)
        log("Ãзавершена сборка через Makefile")
        return

    if cmake_file.exists():

#        tips = advise_missing_bits(cmake_file)
#        if tips:
#            warn(f"Возможны проблемы в CMakeLists.txt:")
#            for t in tips:
#                print(" - " + t.replace("\n", "\n   "))
#            if args.fix_cmake:
#                changed, backup = fix_cmakelists(cmake_file, test_target_hint=args.test_target)
#                if changed:
#                    log(f"CMakeLists.txt обновлён (бэкап: {backup}).")

        # Конфигурация/сборка
        if not args.no_clean and build_dir.exists():
            log(f"Удаление каталог сборки: {build_dir}")
            shutil.rmtree(build_dir)
        build_dir.mkdir(parents=True, exist_ok=True)

        log("Конфигурация CMake…")
        configure(project_dir, build_dir, args.build_type, enable_coverage=not args.no_coverage)

        log("Соборка проекта…")
        build(build_dir, args.jobs)

        log("Запуск тестов (CTest)…")
        run_ctest(build_dir)

        log("Сборка покрытия lcov и генерация HTML…")
        index = collect_coverage(build_dir, args.remove)
        log(f"Отчёт: {index}")

        if not args.no_open and index.exists():
            log("Открытие отчёта в браузере…")
            open_report(index)

        log("Готово")
        return

    if has_make:
        build_with_make(project_dir)
        log("Сборка через makefile")
        return

    err("Не найден ни CmakeLists.txt, ни Makefile")

if __name__ == "__main__":
    main()
