
import tempfile

from ansys.pyaedt.examples.constants import AEDT_VERSION
from pyaedt import Maxwell3d
import ansys.mechanical.core

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

non_graphical = False

project_name = "Busbars"
design_name = "1 Maxwell transient"
solver = "Transient"
desktop_version = AEDT_VERSION

m3d = Maxwell3d(specified_version=desktop_version,
                new_desktop_session=False,
                designname=design_name,
                projectname=project_name,
                solution_type=solver,
                non_graphical=non_graphical)

m3d.modeler.model_units = "mm"

electric_frequency = 50
max_current = 50  # A
number_of_el_periods = 1  # 2-3, 1 for testing purposes
time_steps_per_el_period = 20  # >60, less for testing purposes
mesh_size = 1  # element size in bus bars, 1 good size, 3 for testing

m3d["electric_frequency"] = str(electric_frequency) + "Hz"
m3d["electric_period"] = "1.0/electric_frequency" + " s"
m3d["time_step"] = "electric_period / " + str(time_steps_per_el_period) + " s"
m3d["stop_time"] = str(number_of_el_periods) + "*electric_period" + " s"
m3d["max_current"] = str(max_current) + "A"

setup = m3d.create_setup(setupname="Setup1")
setup.props["StopTime"] = m3d["stop_time"]
setup.props["TimeStep"] = m3d["time_step"]

# saving fields not needed for harmonic force calculation
setup.props["SaveFieldsType"] = "Every N Steps"
setup.props["N Steps"] = "1"
setup.props["Steps From"] = "0s"
setup.props["Steps To"] = "stop_time"


bar1 = m3d.modeler.create_box(
    position=[0, 0, 0],
    dimensions_list=[5, 20, 1],
    matname="copper",
    name="bar1"
)

bar2 = m3d.modeler.create_box(
    position=[0, 0, 5],
    dimensions_list=[5, 20, 1],
    matname="copper",
    name="bar2"
)

m3d.modeler.create_region(pad_percent=[300, 300, 0, 0, 300, 300])

m3d.enable_harmonic_force(objects=[bar1, bar2], force_type=2)  # volumetric force (type 2) can be exported
# todo: change the FFT settings and no of exported frequencies

bar1_in = m3d.assign_coil(bar1.faces_on_bounding_box[0], name="Bar1_in")
bar1_out = m3d.assign_coil(bar1.faces_on_bounding_box[1], name="Bar1_out", polarity="Negative")

current_bar1 = "max_current * sin (2*pi*time*electric_frequency)"
m3d.assign_winding(current_value=current_bar1, name="Bar1")
m3d.add_winding_coils(windingname="Bar1", coil_names=["Bar1_in", "Bar1_out"])

m3d.assign_coil(bar2.faces_on_bounding_box[0], name="Bar2_in")
m3d.assign_coil(bar2.faces_on_bounding_box[1], name="Bar2_out", polarity="Negative")

current_bar2 = "max_current * sin (2*pi*time*electric_frequency + 45deg)"
m3d.assign_winding(current_value=current_bar2, name="Bar2")
m3d.add_winding_coils(windingname="Bar2", coil_names=["Bar2_in", "Bar2_out"])


m3d.mesh.assign_length_mesh(
    names=[bar1, bar2],
    maxlength=mesh_size,
    maxel=None,
    meshop_name="bars_" + str(mesh_size) + "mm"
)

m3d.save_project(project_file="D:/BusbarForce/" + project_name + ".aedt")
m3d.mesh.generate_mesh("Setup1")
m3d.analyze_setup()
m3d.export_element_based_harmonic_force(output_directory="D:/BusbarForce/")


#### Mechanical:

#region Context Menu Action
#imported_load_group_53 = analysis_28.AddImportedLoadExternalData()
#endregion

#region UI Action
#external_data_files = Ansys.Mechanical.ExternalData.ExternalDataFileCollection()
#external_data_files.SaveFilesWithProject = False
#external_data_file_1 = Ansys.Mechanical.ExternalData.ExternalDataFile()
#external_data_files.Add(external_data_file_1)
#external_data_file_1.Identifier = "File1"
#external_data_file_1.Description = ""
#external_data_file_1.IsMainFile = False
#external_data_file_1.FilePath= r'D:\BusbarForce\Setup1\DV3\Maxwellharforce.csv'
#external_data_file_1.ImportSettings = Ansys.Mechanical.ExternalData.ImportSettingsFactory.GetSettingsForFormat(MechanicalEnums.ExternalData.ImportFormat.Delimited)
#import_settings = external_data_file_1.ImportSettings
#import_settings.SkipRows = 1
#import_settings.SkipFooter = 0
#import_settings.Delimiter = ","
#import_settings.AverageCornerNodesToMidsideNodes = False
#import_settings.UseColumn(0, MechanicalEnums.ExternalData.VariableType.XCoordinate, "m", "X Coordinate@A")
#import_settings.UseColumn(1, MechanicalEnums.ExternalData.VariableType.YCoordinate, "m", "Y Coordinate@B")
#import_settings.UseColumn(2, MechanicalEnums.ExternalData.VariableType.ZCoordinate, "m", "Z Coordinate@C")
#import_settings.UseColumn(3, MechanicalEnums.ExternalData.VariableType.Volume, "m^3", "Volume@D")
#import_settings.UseColumn(4, MechanicalEnums.ExternalData.VariableType.BodyForceDensity, "N m^-3", "Body Force Density@E")
#import_settings.UseColumn(5, MechanicalEnums.ExternalData.VariableType.BodyForceDensity, "N m^-3", "Body Force Density@F")
#import_settings.UseColumn(6, MechanicalEnums.ExternalData.VariableType.BodyForceDensity, "N m^-3", "Body Force Density@G")
#import_settings.UseColumn(7, MechanicalEnums.ExternalData.VariableType.BodyForceDensity, "N m^-3", "Body Force Density@H")
#import_settings.UseColumn(8, MechanicalEnums.ExternalData.VariableType.BodyForceDensity, "N m^-3", "Body Force Density@I")
#import_settings.UseColumn(9, MechanicalEnums.ExternalData.VariableType.BodyForceDensity, "N m^-3", "Body Force Density@J")
#import_settings.UseColumn(11, MechanicalEnums.ExternalData.VariableType.BodyForceDensity, "N m^-3", "Body Force Density@L")
#import_settings.UseColumn(12, MechanicalEnums.ExternalData.VariableType.BodyForceDensity, "N m^-3", "Body Force Density@M")
#import_settings.UseColumn(13, MechanicalEnums.ExternalData.VariableType.BodyForceDensity, "N m^-3", "Body Force Density@N")
#import_settings.UseColumn(14, MechanicalEnums.ExternalData.VariableType.BodyForceDensity, "N m^-3", "Body Force Density@O")
#import_settings.UseColumn(15, MechanicalEnums.ExternalData.VariableType.BodyForceDensity, "N m^-3", "Body Force Density@P")
#import_settings.UseColumn(16, MechanicalEnums.ExternalData.VariableType.BodyForceDensity, "N m^-3", "Body Force Density@Q")


#imported_load_group_53.ImportExternalDataFiles(external_data_files)
##endregion

##region Context Menu Action
#imported_body_force_density_54 = imported_load_group_53.AddImportedBodyForceDensity()
##endregion

##region Details View Action
#selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
#selection.Ids = [32, 59]
#imported_body_force_density_54.Location = selection
##endregion

##region Context Menu Action
#imported_load_id_list = [54]
#for imported_load_id in imported_load_id_list:
#    imported_load = DataModel.GetObjectById(imported_load_id)
#    imported_load.ImportLoad()
##endregion


