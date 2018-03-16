import vtk
from vtk.numpy_interface import dataset_adapter
from vtk.util import numpy_support
import numpy as np


def init_window():
    import vtk
    # Create the graphics structure. The renderer renders into the render
    # window. The render window interactor captures mouse events and will
    # perform appropriate camera or actor manipulation depending on the
    # nature of the events.
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    # Add the actors to the renderer, set the background and size
    #ren.AddActor(cylinderActor)
    ren.SetBackground(1, 1, 1)
    renWin.SetSize(400, 400)

    # This allows the interactor to initalize itself. It has to be
    # called before an event loop.
    #iren.Initialize()

    # We'll zoom in a little by accessing the camera and invoking a "Zoom"
    # method on it.
    ren.ResetCamera()
    #ren.GetActiveCamera().Zoom(1.5)
    # Start the event loop.
    #iren.Start()
    
    return ren, renWin, iren


def add_field(field, renderer, iso=0.1, k=0):
    
    spacing = np.zeros(3)
    for i in range(3):
        spacing[i] = field.grid.lattice[i,i]/field.grid.nr[i]
    
    iD = vtk.vtkImageData()
    
    field_vtk = numpy_support.numpy_to_vtk(field.ravel(order="F"), deep=True)    
    iD.GetPointData().SetScalars(field_vtk)
    iD.SetOrigin(0.,0.,0.)
    iD.SetSpacing(spacing)
    iD.SetDimensions(field.grid.nr)
   
    contour = vtk.vtkMarchingCubes()
    contour.SetValue(0, iso)
    contour.SetInputData(iD)
   
    
    #stripper = vtk.vtkStripper()
    #stripper.SetInputConnection(contour.GetOutputPort())

    m = vtk.vtkPolyDataMapper()
    m.SetInputConnection(contour.GetOutputPort())
    m.Update()
    m.ScalarVisibilityOff()
    #m.SetInputData(iD)
    
    a = vtk.vtkActor()
    a.SetMapper(m)
    a.GetProperty().SetDiffuseColor(i2color(k))
    a.GetProperty().SetOpacity(0.4)
    #a.GetProperty().EdgeVisibilityOn()
    
    renderer.AddActor(a)
    renderer.ResetCamera()
    #renderer.GetActiveCamera().Zoom(1.0)

    print("Done!")


def add_atom(label, pos, renderer):
    r = 1.0
    ball = vtk.vtkSphereSource()
    ball.SetRadius(label2radius(label))
    ball.SetCenter(pos)

    # The mapper is responsible for pushing the geometry into the graphics
    # library. It may also do color mapping, if scalars or other
    # attributes are defined.
    ballMapper = vtk.vtkPolyDataMapper()
    ballMapper.SetInputConnection(ball.GetOutputPort())

    # The actor is a grouping mechanism: besides the geometry (mapper), it
    # also has a property, transformation matrix, and/or texture map.
    # Here we set its color and rotate it -22.5 degrees.
    ballActor = vtk.vtkActor()
    ballActor.SetMapper(ballMapper)
    #cylinderActor.SetMapper(data_vtk)
    ballActor.GetProperty().SetColor(label2color(label))
    
    renderer.AddActor(ballActor)

    
def label2color(label):
    color_dict = {
        "O": (1.,0.,0.),
        "H": (0.9,0.9,0.9)
    }
    if label in color_dict:
        return color_dict[label]
    return (.5,.5,.5)

def label2radius(label):
    radius_dict = {
        "O": 0.5,
        "H": 0.25
    }
    if label in radius_dict:
        return radius_dict[label]
    return 0.5

def i2color(i):
    n = 6
    j = i%n
    colors = [
        (1.,0.,0.),
        (0.,1.,0.),
        (0.,0.,1.),
        (1.,1.,0.),
        (1.,0.,1.),
        (0.,1.,1.),
    ]
    return colors[j]

def render_pp(filename):
    from pbcpy.formats.qepp import PP
    system = PP(filename).read()
    render_system(system)
    
def render_system(system):
    ren, win, iren = init_window()
    
    for atom in system.ions:
        add_atom(atom.label, atom.pos, ren)
        
    iso = 0.1
    i = 6
    add_field(system.field, ren, iso, i)
    
    iren.Initialize()
    win.Render()
    iren.Start()
    
    win.Finalize()
    iren.TerminateApp()
    del win, iren

