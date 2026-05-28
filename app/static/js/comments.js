// Section-targeted comments
// Click on any section (paragraph, heading, etc.) to open the comment form for it.

document.addEventListener('DOMContentLoaded', function() {
    const formContainer = document.getElementById('comment-form-container');
    if (!formContainer) return;

    const sectionInput = document.getElementById('comment-section-id');
    const sectionLabel = document.getElementById('comment-section-label');
    const cancelBtn = document.getElementById('comment-cancel');

    // Find all commentable sections (elements with data-section attribute)
    const sections = document.querySelectorAll('[data-section]');

    sections.forEach(function(section) {
        section.classList.add('commentable');
        section.addEventListener('click', function(e) {
            // Don't trigger if clicking a link inside the section
            if (e.target.tagName === 'A') return;

            const sectionId = section.getAttribute('data-section');
            sectionInput.value = sectionId;
            sectionLabel.textContent = sectionId;

            // Position form near the section
            section.after(formContainer);
            formContainer.classList.remove('hidden');
            formContainer.querySelector('textarea').focus();
        });
    });

    // Cancel button hides the form
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            formContainer.classList.add('hidden');
        });
    }

    // Highlight sections that have comments
    const comments = document.querySelectorAll('.comment[data-section]');
    comments.forEach(function(comment) {
        const sectionId = comment.getAttribute('data-section');
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.add('has-comments');
        }
    });
});
