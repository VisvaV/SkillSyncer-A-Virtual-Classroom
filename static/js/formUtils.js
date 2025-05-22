// formUtils.js - Handles form-related interactivity and animations

document.addEventListener('DOMContentLoaded', function () {
    // Form Field Focus Animation
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('focus', function () {
            this.style.borderColor = '#106EBE';
            this.style.boxShadow = '0 0 15px #0FFCBE';
            this.style.transform = 'scale(1.02)';
            this.style.transition = 'all 0.3s ease';
        });
        input.addEventListener('blur', function () {
            this.style.borderColor = '#e0f8f5';
            this.style.boxShadow = 'none';
            this.style.transform = 'scale(1)';
        });
    });

    // Role Toggle for Register Page (if applicable)
    const roleSelect = document.getElementById('roleSelect');
    const studentFields = document.getElementById('studentFields');
    const teacherFields = document.getElementById('teacherFields');

    if (roleSelect) {
        roleSelect.addEventListener('change', function () {
            const role = this.value;
            if (studentFields && teacherFields) {
                studentFields.style.display = role === 'Student' ? 'block' : 'none';
                studentFields.classList.add('animate__fadeIn');
                teacherFields.style.display = role === 'Teacher' ? 'block' : 'none';
                teacherFields.classList.add('animate__fadeIn');
                setTimeout(() => {
                    studentFields.classList.remove('animate__fadeIn');
                    teacherFields.classList.remove('animate__fadeIn');
                }, 500); // Match fadeIn duration
            }
        });
    }

    // Form Submission Animation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.style.opacity = '0.7';
                submitButton.style.transform = 'scale(0.95)';
                submitButton.style.transition = 'all 0.3s ease';
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.style.opacity = '1';
                    submitButton.style.transform = 'scale(1)';
                }, 2000); // Simulate submission feedback
            }
        });
    });

    // Ensure Quiz Submission Validation
    const quizForms = document.querySelectorAll('form[action^="/submit_quiz"]');
    quizForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const questions = document.querySelectorAll('[name^="question_"]');
            let allAnswered = true;
            questions.forEach(q => {
                if (!document.querySelector(`input[name="${q.name}"]:checked`)) {
                    allAnswered = false;
                }
            });
            if (!allAnswered) {
                e.preventDefault();
                alert('Please answer all questions before submitting.');
                questions.forEach(q => {
                    if (!document.querySelector(`input[name="${q.name}"]:checked`)) {
                        q.parentElement.classList.add('animate__shakeX');
                        setTimeout(() => {
                            q.parentElement.classList.remove('animate__shakeX');
                        }, 500); // Match shakeX duration
                    }
                });
            }
        });
    });
});