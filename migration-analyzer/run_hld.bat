@echo off
echo Running Sprint 3 HLD Generation
echo ================================

REM Check if Sprint 2 data exists
if not exist "sprint2_output\sprint2_analysis.json" (
    echo Error: Sprint 2 data not found. Please run Sprint 2 first.
    echo Expected file: sprint2_output\sprint2_analysis.json
    pause
    exit /b 1
)

echo Found Sprint 2 data. Starting HLD generation...
echo.

REM Run the HLD generation
python run_hld_generation.py --sprint2-data sprint2_output\sprint2_analysis.json --output-dir sprint3_output

if errorlevel 1 (
    echo.
    echo HLD generation failed!
    pause
    exit /b 1
)

echo.
echo HLD generation completed successfully!
echo Check sprint3_output\ for generated documents:
echo   - High_Level_Design.md
echo   - hld_data.json
echo.
pause 