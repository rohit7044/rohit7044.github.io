# Visual and interaction specification

Matte charcoal #10100F; secondary surface #1B1B19; dividers #33322F; primary text #EEEAE2; secondary text #ABA69D; sand #C5B49C.

System Arial/Helvetica for navigation and body copy; Georgia italic for editorial emphasis. Fonts are local, avoiding external requests and failures offline. Main content is bounded at 1440px with 5% margins (6% mobile). Sections use 100px vertical spacing, reduced to 65px on mobile. Hairline dividers establish hierarchy without ornamental effects.

Desktop has a two-column hero and three-column research grid. Tablet uses two research columns. At 650px the hero, research, education and timeline become single-column; navigation becomes an explicitly toggled menu.

The independent face viewer uses restrained clay shading, bounded yaw ±0.65 radians and pitch ±0.25, damped manual movement and no camera zoom or ambient motion. Arrow keys support rotation. Reset restores the initial three-quarter view. Mode buttons expose pressed state. Official GNM expression controls offer Open mouth, Smile, Pucker and Left wink. Surface restores neutral. Teeth and gums remain in the mesh; no separate anatomy control is exposed. Topology, Wide smile and the metadata paragraph below the render are omitted per the user's final preference. Reduced motion, missing assets, context loss and WebGL failure show the actual-head poster and disable interactive controls.

Rendering is demand-driven and paused offscreen; device pixel ratio is capped at 1.5. Phone headings scale down to fit 320px screens, footer content wraps, and interactive controls provide 44px touch targets. Browser checks cover 320, 360, 390, 414, 768 and 1440px widths.
