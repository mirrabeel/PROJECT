document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('search-form').addEventListener('submit', searchProjects);
});

function searchProjects(event) {
    event.preventDefault();
    
    const query = document.getElementById('searchQuery').value.toLowerCase();
    const projects = [
        'წიგნების თაროს სასკოლო სეზონი',
        'გაცვლითი პროექტი შვედეთში',
        'გაცვლითი პროექტი ესპანეთში',
        'სასწავლო პროგრამა სილიკონ ველზე',
        'გაცვლით პროგრამა დანიასა და სომხეთში',
        'თბილისის ქალთა ლიდერობის აკადემია'
    ];
    
    const results = projects.filter(project => project.toLowerCase().includes(query));
    
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '';
    
    if (results.length > 0) {
        results.forEach(result => {
            const li = document.createElement('li');
            li.textContent = result;
            resultsContainer.appendChild(li);
        });
    } else {
        resultsContainer.innerHTML = '<li>არ მოიძებნა</li>';
    }
}