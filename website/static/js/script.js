<script>
  const blendRadio = document.getElementById("Blend");
  const batchRadio = document.getElementById("Batch");
  const numberLabel = document.getElementById("numberLabel");

  blendRadio.addEventListener("change", function() {
    numberLabel.textContent = "Blend Number";
  });

  batchRadio.addEventListener("change", function() {
    numberLabel.textContent = "Batch Number";
  });
// Used for traceback function 
// Retrieve the blend history data from the server
// Retrieve the blend history data from the server
fetch('/TraceBack')
  .then(response => response.json())
  .then(data => {
    // Create the tree layout
    var treeLayout = d3.tree().size([600, 400]);

    // Create the SVG container for the tree
    var svg = d3.select("#tree-container").append("svg")
      .attr("width", 800)
      .attr("height", 600)
      .append("g")
      .attr("transform", "translate(50,50)");

    // Create a hierarchy from the blend history data
    var root = d3.hierarchy(data);

    // Assign coordinates to each node in the tree
    treeLayout(root);

    // Create links between nodes
    svg.selectAll(".link")
      .data(root.links())
      .enter()
      .append("path")
      .attr("class", "link")
      .attr("d", d3.linkHorizontal()
        .x(function(d) { return d.y; })
        .y(function(d) { return d.x; }));

    // Create nodes
    var nodes = svg.selectAll(".node")
      .data(root.descendants())
      .enter()
      .append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

    // Add circles to represent nodes
    nodes.append("circle")
      .attr("r", 4.5);

    // Add labels to nodes
    nodes.append("text")
      .attr("dy", ".35em")
      .attr("x", function(d) { return d.children ? -13 : 13; })
      .style("text-anchor", function(d) { return d.children ? "end" : "start"; })
      .text(function(d) { return d.data.name; });
  });


</script>