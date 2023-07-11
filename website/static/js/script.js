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

  function updateFormAction(event) {
    let form = document.getElementById('facilityForm');
    let selectedOption = event.target.value;
    form.action = '/builds/' + selectedOption;
  }
</script>