
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
</script>
