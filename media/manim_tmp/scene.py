from manim import *

class SimpleSineWave(Scene):
    def construct(self):
        # Create a number plane
        axes = NumberPlane(
            x_range=[-5, 5, 1],
            y_range=[-2, 2, 1],
            background_line_style={
                "stroke_color": BLUE_D,
                "stroke_width": 1,
                "stroke_opacity": 0.5
            }
        )
        
        # Create the sine function graph
        sine_function = axes.plot(
            lambda x: np.sin(x),
            x_range=[-5, 5],
            color=YELLOW
        )
        
        # Create a function label
        function_label = Text("y = sin(x)", color=YELLOW).scale(0.7)
        function_label.to_corner(UR).shift(DOWN + LEFT)
        
        # Draw everything
        self.play(Create(axes))
        self.play(Create(sine_function))
        self.play(Write(function_label))
        
        # Create a dot to move along the sine wave
        dot = Dot(color=RED)
        dot.move_to(axes.c2p(-5, np.sin(-5)))
        
        self.play(Create(dot))
        
        # Move the dot along the sine wave
        self.play(
            dot.animate.move_to(axes.c2p(5, np.sin(5))),
            rate_func=linear,
            run_time=6
        )
        
        self.wait(1)