let previewContainer = document.querySelector('.products-preview');
let previewBox = previewContainer.querySelectorAll('.preview');

document.querySelectorAll('.pro-container .pro').forEach(pro => {
  pro.onclick = () => {
    previewContainer.style.display = 'flex';
    let name = pro.getAttribute('data-name');
    previewBox.forEach(preview => {
      let target = preview.getAttribute('data-target');
      if (name == target) {
        preview.classList.add('active');
      }
    });
  };
});

previewBox.forEach(close => {
  close.querySelector('.fa-times').onclick = () => {
    close.classList.remove('active');
    previewContainer.style.display = 'none';
  };
});



// let previewContainer = document.querySelector('.products-preview');
// let previewBox = previewContainer.querySelectorAll('.preview');

// document.querySelectorAll('.pro-container .pro').forEach(pro => {
//   pro.onclick = () => {
//     previewContainer.style.display = 'flex';
//     let name = pro.getAttribute('data-name');
//     previewBox.forEach(preview => {
//       let target = preview.getAttribute('data-target');
//       if (name === target) {
//         preview.classList.add('active');
//       }
//     });
//   };
// });

// previewBox.forEach(close => {
//   close.querySelector('.fa-times').onclick = () => {
//     close.classList.remove('active');
//     previewContainer.style.display = 'none';
//   };
// });