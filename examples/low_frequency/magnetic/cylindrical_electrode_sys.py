"""
PyAEDT Example: Cylindrical Electrode System - Electrostatic Analysis

This script demonstrates how to create a cylindrical electrode system using PyAEDT:
- Creates inner and outer electrodes with insulation layer
- Sets up an electrostatic analysis in Maxwell 2D
- Applies voltage boundaries
- Runs the simulation
- Exports results to CSV
"""
import os

import ansys.aedt.core as aedt_app

# Project and output settings
OUTPUT_DIR = "D:/Local_example_w"
PROJECT_NAME = "Cylindrical_Electrode"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create or open Maxwell 2D design
m2d = aedt_app.Maxwell2d()

# Set solution type and units
m2d.solution_type = "Electrostatic"
aedt_app.modeler.model_units = "cm"
aedt_app.modeler.model_coordinate_system.depth = "10000cm"


def save_project(self, project_name=None, project_path=None):
    """Save the current project to the specified path."""
    if project_path is None:
        project_path = os.path.join(OUTPUT_DIR, f"{PROJECT_NAME}.aedt")
    self.odesktop.SaveProjectAs(project_path)
    return project_path


project_path = os.path.join(OUTPUT_DIR, f"{PROJECT_NAME}.aedt")
m2d.save_project(project_path)

# Create geometry: Inner Electrode (Circle with radius 5cm)
inner_electrode = m2d.modeler.create_circle(center_point=[0, 0, 0], radius=5, material="copper", name="inner_electrode")
inner_electrode.color = (255, 255, 0)
inner_electrode.transparency = 0.59

# Create geometry: Outer Layer (Circle with radius 10cm)
outer_layer = m2d.modeler.create_circle(center_point=[0, 0, 0], radius=10, material="air", name="outer_layer")

# Create geometry: Outer Electrode (Circle with radius 11cm)
outer_electrode = m2d.modeler.create_circle(center_point=[0, 0, 0], radius=11, material="copper", name="outer_electrode_temp")

# Perform boolean operations to create the layered structure
# Subtract inner from outer_layer to create insulation
m2d.modeler.subtract(blank_part=outer_layer, tool_part=inner_electrode, keep_originals=True)

# Rename outer_layer to insulation after subtraction
outer_layer.name = "insulation"
outer_layer.color = (128, 255, 0)
outer_layer.transparency = 0.2

# Subtract inner and insulation from outer_electrode to create final outer electrode
m2d.modeler.subtract(blank_part=outer_electrode, tool_part=[inner_electrode, outer_layer], keep_originals=True)
outer_electrode.name = "outer_electrode"
outer_electrode.color = (255, 255, 0)

# Create region (simulation domain)
m2d.modeler.create_region(padding_percentage=0, name="Region")

# Save project after geometry creation
m2d.save_project()

# Add boundary conditions: Voltage assignments
boundary_setup = m2d.modeler.odesign.GetModule("BoundarySetup")

boundary_setup.AssignVoltage(["NAME:Inner_Voltage", "Objects:=", ["inner_electrode"], "Value:=", "100kV", "CoordinateSystem:=", ""])

boundary_setup.AssignVoltage(["NAME:Outer_Voltage", "Objects:=", ["outer_electrode"], "Value:=", "0V", "CoordinateSystem:=", ""])

# Set up Maxwell parameters
maxwell_setup = m2d.modeler.odesign.GetModule("MaxwellParameterSetup")

maxwell_setup.AssignForce(["NAME:Force1", "Reference CS:=", "Global", "Objects:=", ["inner_electrode"]])

maxwell_setup.AssignMatrix(
    [
        "NAME:Matrix1",
        ["NAME:MatrixEntry", ["NAME:MatrixEntry", "Source:=", "Inner_Voltage", "NumberOfTurns:=", "1"], ["NAME:MatrixEntry", "Source:=", "Outer_Voltage", "NumberOfTurns:=", "1"]],
        ["NAME:MatrixGroup"],
        "GroundSources:=",
        "",
    ]
)

# Create analysis setup
analysis_setup = m2d.modeler.odesign.GetModule("AnalysisSetup")

analysis_setup.InsertSetup(
    "Electrostatic",
    [
        "NAME:Setup1",
        "Enabled:=",
        True,
        ["NAME:MeshLink", "ImportMesh:=", False],
        "MaximumPasses:=",
        10,
        "MinimumPasses:=",
        2,
        "MinimumConvergedPasses:=",
        1,
        "PercentRefinement:=",
        50,
        "SolveFieldOnly:=",
        False,
        "PercentError:=",
        0.5,
        "SolveMatrixAtLast:=",
        True,
        "UseNonLinearIterNum:=",
        False,
        "CacheSaveKind:=",
        "Delta",
        "ConstantDelta:=",
        "0s",
        "NonLinearResidual:=",
        0.001,
        "RelaxationFactor:=",
        1,
    ],
)

# Save project before analysis
m2d.save_project()

# Run analysis
m2d.analyze_nominal()

# Create field plots
fields_reporter = m2d.modeler.odesign.GetModule("FieldsReporter")

# Create voltage field plot
fields_reporter.CreateFieldPlot(
    [
        "NAME:Voltage1",
        "SolutionName:=",
        "Setup1 : LastAdaptive",
        "UserSpecifyName:=",
        0,
        "UserSpecifyFolder:=",
        0,
        "QuantityName:=",
        "Voltage",
        "PlotFolder:=",
        "Voltage",
        "StreamlinePlot:=",
        False,
        "AdjacentSidePlot:=",
        False,
        "FullModelPlot:=",
        False,
        "IntrinsicVar:=",
        "",
        "PlotGeomInfo:=",
        [1, "Surface", "FacesList", 1, "insulation"],
        "FilterBoxes:=",
        [1, "insulation"],
        [
            "NAME:PlotOnSurfaceSettings",
            "ShadingType:=",
            0,
            "Filled:=",
            False,
            "IsoValType:=",
            "Tone",
            "AddGrid:=",
            False,
            "MapTransparency:=",
            True,
            "Refinement:=",
            0,
            "Transparency:=",
            0,
            "SmoothingLevel:=",
            0,
            ["NAME:Arrow3DSpacingSettings", "ArrowUniform:=", True, "ArrowSpacing:=", 0, "MinArrowSpacing:=", 0, "MaxArrowSpacing:=", 0],
            "GridColor:=",
            [255, 255, 255],
        ],
        "EnableGaussianSmoothing:=",
        False,
        "SurfaceOnly:=",
        False,
    ],
    "Field",
)

# Configure voltage plot settings
fields_reporter.SetPlotFolderSettings(
    "Voltage",
    [
        "NAME:FieldsPlotSettings",
        "Real time mode:=",
        True,
        ["NAME:ColorMapSettings", "ColorMapType:=", "Spectrum", "SpectrumType:=", "Rainbow", "UniformColor:=", [127, 255, 255], "RampColor:=", [255, 127, 127]],
        [
            "NAME:Scale3DSettings",
            "unit:=",
            68,
            "m_nLevels:=",
            10,
            "minvalue:=",
            0,
            "maxvalue:=",
            100000,
            "log:=",
            False,
            "IntrinsicMin:=",
            0,
            "IntrinsicMax:=",
            100000,
            "LimitFieldValuePrecision:=",
            False,
            "FieldValuePrecisionDigits:=",
            4,
            "dB:=",
            False,
            "AnimationStaticScale:=",
            False,
            "ScaleType:=",
            0,
            "UserSpecifyValues:=",
            [11, 0, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000],
            "ValueNumberFormatTypeAuto:=",
            0,
            "ValueNumberFormatTypeScientific:=",
            False,
            "ValueNumberFormatWidth:=",
            11,
            "ValueNumberFormatPrecision:=",
            3,
        ],
        ["NAME:Marker3DSettings", "MarkerType:=", 0, "MarkerMapSize:=", False, "MarkerMapColor:=", False, "MarkerSize:=", 0.25],
        [
            "NAME:Arrow3DSettings",
            "ArrowType:=",
            1,
            "ArrowMapSize:=",
            False,
            "ArrowMapColor:=",
            True,
            "ShowArrowTail:=",
            True,
            "ArrowSize:=",
            0.1,
            "ArrowMinMagnitude:=",
            -0.5,
            "ArrowMaxMagnitude:=",
            100000.5,
            "ArrowMagnitudeThreshold:=",
            0,
            "ArrowMagnitudeFilteringFlag:=",
            False,
            "ArrowMinIntrinsicMagnitude:=",
            0,
            "ArrowMaxIntrinsicMagnitude:=",
            1,
        ],
        ["NAME:DeformScaleSettings", "ShowDeformation:=", True, "MinScaleFactor:=", 0, "MaxScaleFactor:=", 1, "DeformationScale:=", 0, "ShowDeformationOutline:=", False],
    ],
)

# Create electric field magnitude plot
fields_reporter.CreateFieldPlot(
    [
        "NAME:Mag_E1",
        "SolutionName:=",
        "Setup1 : LastAdaptive",
        "UserSpecifyName:=",
        0,
        "UserSpecifyFolder:=",
        0,
        "QuantityName:=",
        "Mag_E",
        "PlotFolder:=",
        "E",
        "StreamlinePlot:=",
        False,
        "AdjacentSidePlot:=",
        False,
        "FullModelPlot:=",
        False,
        "IntrinsicVar:=",
        "",
        "PlotGeomInfo:=",
        [1, "Surface", "FacesList", 1, "insulation"],
        "FilterBoxes:=",
        [1, "insulation"],
        [
            "NAME:PlotOnSurfaceSettings",
            "ShadingType:=",
            0,
            "Filled:=",
            False,
            "IsoValType:=",
            "Tone",
            "AddGrid:=",
            False,
            "MapTransparency:=",
            True,
            "Refinement:=",
            0,
            "Transparency:=",
            0,
            "SmoothingLevel:=",
            0,
            ["NAME:Arrow3DSpacingSettings", "ArrowUniform:=", True, "ArrowSpacing:=", 0, "MinArrowSpacing:=", 0, "MaxArrowSpacing:=", 0],
            "GridColor:=",
            [255, 255, 255],
        ],
        "EnableGaussianSmoothing:=",
        False,
        "SurfaceOnly:=",
        False,
    ],
    "Field",
)

# Create polyline for field extraction
polyline = m2d.modeler.create_polyline(points=[[5, 0, 0], [10, 0, 0]], name="Polyline1", segment_type="Line")

# Create reports for data extraction
report_setup = m2d.modeler.odesign.GetModule("ReportSetup")

# Create voltage report along polyline
report_setup.CreateReport(
    "Calculator Expressions Plot1",
    "Fields",
    "Rectangular Plot",
    "Setup1 : LastAdaptive",
    ["Context:=", "Polyline1", "PointCount:=", 101],
    ["Distance:=", ["All"]],
    ["X Component:=", "Distance", "Y Component:=", ["Voltage"]],
)

# Create electric field magnitude report along polyline
report_setup.CreateReport(
    "Calculator Expressions Plot2",
    "Fields",
    "Rectangular Plot",
    "Setup1 : LastAdaptive",
    ["Context:=", "Polyline1", "PointCount:=", 101],
    ["Distance:=", ["All"]],
    ["X Component:=", "Distance", "Y Component:=", ["Mag_E"]],
)

# Export report to CSV file
csv_file_path = os.path.join(OUTPUT_DIR, "Calculator Expressions Plot2.csv")
report_setup.ExportToFile("Calculator Expressions Plot2", csv_file_path, False)

# Final save
m2d.save_project()

print(f" Project saved: {project_path}")
print(f" Results exported to: {csv_file_path}")
print(f" Analysis completed successfully!")
