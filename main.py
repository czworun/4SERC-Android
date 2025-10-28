# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.scatter import Scatter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io

class SERC4DEnvironment:
    def __init__(self):
        self.g = np.array([
            [1, -1/4, -1/4, -1/4],
            [-1/4, 1, -1/4, -1/4],
            [-1/4, -1/4, 1, -1/4],
            [-1/4, -1/4, -1/4, 1]
        ])
        self.base_tetrahedron = self.create_regular_tetrahedron_4d()
    
    def create_regular_tetrahedron_4d(self, edge_length=1.0):
        s = np.sqrt(edge_length / 2.5)
        vertices = np.array([
            [s, 0, 0, 0],    # S
            [0, s, 0, 0],    # E  
            [0, 0, s, 0],    # R
            [0, 0, 0, s]     # C
        ])
        return vertices
    
    def rotate_4d(self, points, angle_xy=0, angle_xz=0, angle_xw=0):
        def rotation_matrix(axis1, axis2, angle):
            mat = np.eye(4)
            mat[axis1, axis1] = np.cos(angle)
            mat[axis1, axis2] = -np.sin(angle)
            mat[axis2, axis1] = np.sin(angle)
            mat[axis2, axis2] = np.cos(angle)
            return mat
        
        R = np.eye(4)
        if angle_xy != 0: R = R @ rotation_matrix(0, 1, angle_xy)
        if angle_xz != 0: R = R @ rotation_matrix(0, 2, angle_xz)
        if angle_xw != 0: R = R @ rotation_matrix(0, 3, angle_xw)
        
        return points @ R.T
    
    def project_to_3d(self, points_4d):
        # Uproszczona projekcja perspektywiczna
        points_3d = []
        for point in points_4d:
            w = point[3]
            scale = 2.0 / (2.0 + w) if w > -2 else 0.1
            points_3d.append(point[:3] * scale)
        return np.array(points_3d)

class SERCApp(App):
    def __init__(self):
        super().__init__()
        self.env = SERC4DEnvironment()
        self.current_tetra = self.env.base_tetrahedron
        self.rotation_angles = [0, 0, 0]  # xy, xz, xw
        
    def build(self):
        # Główny layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Nagłówek
        title = Label(
            text='[b]4SERC Modeler[/b] - Leszek Papiernik',
            markup=True,
            size_hint=(1, 0.1),
            color=[1, 1, 1, 1]
        )
        main_layout.add_widget(title)
        
        # Obszar wizualizacji
        self.image_widget = Image(size_hint=(1, 0.6))
        main_layout.add_widget(self.image_widget)
        
        # Kontrolki obrotu
        controls_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.3))
        
        # Suwak XY
        xy_slider_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        xy_slider_layout.add_widget(Label(text='Obrót XY:', size_hint=(0.3, 1)))
        self.xy_slider = Slider(min=-3.14, max=3.14, value=0, size_hint=(0.7, 1))
        self.xy_slider.bind(value=self.on_xy_rotate)
        xy_slider_layout.add_widget(self.xy_slider)
        controls_layout.add_widget(xy_slider_layout)
        
        # Suwak XZ
        xz_slider_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        xz_slider_layout.add_widget(Label(text='Obrót XZ:', size_hint=(0.3, 1)))
        self.xz_slider = Slider(min=-3.14, max=3.14, value=0, size_hint=(0.7, 1))
        self.xz_slider.bind(value=self.on_xz_rotate)
        xz_slider_layout.add_widget(self.xz_slider)
        controls_layout.add_widget(xz_slider_layout)
        
        # Suwak XW (wymiar C)
        xw_slider_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        xw_slider_layout.add_widget(Label(text='Wymiar C:', size_hint=(0.3, 1)))
        self.xw_slider = Slider(min=-3.14, max=3.14, value=0, size_hint=(0.7, 1))
        self.xw_slider.bind(value=self.on_xw_rotate)
        xw_slider_layout.add_widget(self.xw_slider)
        controls_layout.add_widget(xw_slider_layout)
        
        main_layout.add_widget(controls_layout)
        
        # Przyciski akcji
        buttons_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        btn_tetra = Button(text='Pojedynczy', on_press=self.show_single)
        buttons_layout.add_widget(btn_tetra)
        
        btn_helix = Button(text='Tetraheliks', on_press=self.show_helix)
        buttons_layout.add_widget(btn_helix)
        
        btn_reset = Button(text='Reset', on_press=self.reset_view)
        buttons_layout.add_widget(btn_reset)
        
        main_layout.add_widget(buttons_layout)
        
        # Inicjalna wizualizacja
        Clock.schedule_once(lambda dt: self.update_visualization(), 0.1)
        
        return main_layout
    
    def on_xy_rotate(self, instance, value):
        self.rotation_angles[0] = value
        self.update_visualization()
    
    def on_xz_rotate(self, instance, value):
        self.rotation_angles[1] = value
        self.update_visualization()
    
    def on_xw_rotate(self, instance, value):
        self.rotation_angles[2] = value
        self.update_visualization()
    
    def show_single(self, instance):
        self.current_tetra = self.env.base_tetrahedron
        self.update_visualization()
    
    def show_helix(self, instance):
        # Prosty tetraheliks
        tetrahedra = []
        for i in range(5):
            tetra = self.env.rotate_4d(
                self.env.base_tetrahedron, 
                angle_xy=i * 0.5,
                angle_xz=i * 0.3
            )
            tetra[:, 2] += i * 0.5  # Przesunięcie wzdłuż Z
            tetrahedra.append(tetra)
        
        # Połącz wszystkie czworościany
        self.current_tetra = np.vstack(tetrahedra)
        self.update_visualization()
    
    def reset_view(self, instance):
        self.rotation_angles = [0, 0, 0]
        self.xy_slider.value = 0
        self.xz_slider.value = 0
        self.xw_slider.value = 0
        self.current_tetra = self.env.base_tetrahedron
        self.update_visualization()
    
    def update_visualization(self):
        # Obróć czworościan
        rotated_tetra = self.env.rotate_4d(
            self.current_tetra,
            angle_xy=self.rotation_angles[0],
            angle_xz=self.rotation_angles[1], 
            angle_xw=self.rotation_angles[2]
        )
        
        # Projekcja do 3D
        tetra_3d = self.env.project_to_3d(rotated_tetra)
        
        # Stwórz wykres matplotlib
        fig = plt.figure(figsize=(6, 6), dpi=80)
        ax = fig.add_subplot(111, projection='3d')
        
        # Rysuj krawędzie jeśli to pojedynczy czworościan
        if len(tetra_3d) == 4:
            edges = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
            for edge in edges:
                points = tetra_3d[list(edge)]
                ax.plot3D(points[:,0], points[:,1], points[:,2], 'blue', linewidth=3)
        
        # Rysuj wierzchołki
        colors = ['red', 'green', 'blue', 'purple']
        labels = ['S', 'E', 'R', 'C']
        
        for i in range(len(tetra_3d)):
            color = colors[i % 4]
            label = labels[i % 4] if i < 4 else ''
            
            ax.scatter3D(
                tetra_3d[i,0], tetra_3d[i,1], tetra_3d[i,2], 
                c=color, s=100, depthshade=True
            )
            
            if label:
                ax.text(
                    tetra_3d[i,0], tetra_3d[i,1], tetra_3d[i,2],
                    label, fontsize=12, ha='center', va='center'
                )
        
        ax.set_xlim([-2, 2])
        ax.set_ylim([-2, 2]) 
        ax.set_zlim([-2, 2])
        ax.set_xlabel('S')
        ax.set_ylabel('E')
        ax.set_zlabel('R')
        ax.set_title('Metryka 4SERC')
        
        # Konwertuj do tekstury Kivy
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        
        buf = np.frombuffer(canvas.tostring_rgb(), dtype=np.uint8)
        buf = buf.reshape(canvas.get_width_height()[::-1] + (3,))
        
        texture = Texture.create(size=(buf.shape[1], buf.shape[0]))
        texture.blit_buffer(buf.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        
        self.image_widget.texture = texture
        plt.close(fig)

if __name__ == '__main__':
    SERCApp().run()
