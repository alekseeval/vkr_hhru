$(document).ready(function() {

    let form = document.querySelector('form')
    form.addEventListener('submit', function (event) {
        event.preventDefault()
        console.log('clicked on validate')
        post_data()
    })

    function post_data(){

        let href = 'http://127.0.0.1:8000/app/resume/save?'

        href += 'id=' + $('#id').text() + '&'

        href += 'last_name=' + $('#last_name').val() + '&'
        href += 'first_name=' + $('#first_name').val() + '&'
        href += 'middle_name=' + $('#second_name').val() + '&'

        href += 'title=' + $('#title').val() + '&'
        href += 'salary_amount=' + $('#salary-amount').val() + '&'
        href += 'salary_currency=' + $('#salary-currency').val() + '&'
        href += 'birth_date=' + $('#birth_date').val() + '&'

        href += 'skills=' + $('#skills').val()

        location.href = href

    }
});

