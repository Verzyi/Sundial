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

  // Function to automatically fade out flash messages after a few seconds
  function fadeOutFlashMessages() {
        const flashMessages = document.querySelectorAll('.alert-dismissible');

        flashMessages.forEach((message) => {
    setTimeout(() => {
      message.classList.add('fade');
      setTimeout(() => {
        message.style.display = 'none';
      }, 500); // Adjust the duration (in milliseconds) for how long the message stays visible before fading out
    }, 3000); // Adjust the duration (in milliseconds) for how long the message stays visible before starting to fade out
        });
    }

  // Call the function to fade out flash messages when the page finishes loading
  window.addEventListener('load', fadeOutFlashMessages);

</script>