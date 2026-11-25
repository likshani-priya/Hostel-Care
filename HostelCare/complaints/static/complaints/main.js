document.addEventListener('DOMContentLoaded', function() {
    // 1. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 2. Auto scroll chat container to bottom
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // 3. Dynamic layout updates for student/warden registration
    const roleSelect = document.getElementById('id_role');
    if (roleSelect) {
        const studentFields = ['id_roll_no', 'id_room_no', 'id_hostel_block'];
        
        function toggleStudentFields() {
            const isStudent = roleSelect.value === 'student';
            studentFields.forEach(fieldId => {
                const fieldInput = document.getElementById(fieldId);
                if (fieldInput) {
                    const row = fieldInput.closest('.mb-3') || fieldInput.parentElement;
                    if (row) {
                        if (isStudent) {
                            row.style.display = 'block';
                            fieldInput.setAttribute('required', 'required');
                        } else {
                            row.style.display = 'none';
                            fieldInput.removeAttribute('required');
                        }
                    }
                }
            });
        }

        // Toggle on page load & on change
        toggleStudentFields();
        roleSelect.addEventListener('change', toggleStudentFields);
    }
});
