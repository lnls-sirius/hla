
graph_x = display.getWidget("Graph Orbit X")
graph_y = display.getWidget("Graph Orbit Y")

ax = graph_x.figure.XYGraph.getXAxisList()[0]
ax.setMinorTicksVisible(0)
ax.setMajorTickMarkStepHint(60)

ax = graph_y.figure.XYGraph.getXAxisList()[0]
ax.setMinorTicksVisible(0)
ax.setMajorTickMarkStepHint(60)