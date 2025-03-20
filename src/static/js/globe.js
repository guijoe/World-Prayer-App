

let globe, countries = [], autoRotate = true, highlightedCountry = null, rightPanel, leftPanel;

function createGlobe() {
    globe = new Globe()
        (document.getElementById('globeViz'))
        .globeImageUrl('https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-night.jpg')
        .bumpImageUrl('https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-topology.png')
        .backgroundImageUrl('https://cdn.jsdelivr.net/npm/three-globe/example/img/night-sky.png')
        .polygonAltitude(0.06)
        .polygonCapColor(() => 'rgba(200, 200, 200, 0.3)')
        .polygonSideColor(() => 'rgba(0, 100, 0, 0.15)')
        .polygonStrokeColor(() => '#111')
        ;
    
    //globe.centerAt([40.7128, -74.0060]);
    
    //console.log(globe)
    globe.atmosphereColor('lightskyblue').atmosphereAltitude(0.25);
    
    const globeContainer = document.getElementById('globeContainer');
    
    if (window.innerWidth <= 768) {
        globe.camera().position.set(0, 0, 600); // Increase Z value for a smaller globe
    }
    else {
      // Default settings for larger screens
      //globe.camera().fov = 30;
      //globe.camera().position.set(0, 0, 800);
    }

    // Update the camera after making changes
    globe.camera().updateProjectionMatrix();
    
    //globe.rendererConfig({ antialias: true, alpha: true });
}

function createPanels() {
    const mainContent = document.getElementById('main-content');
    leftPanel = document.getElementById('left-panel');
    rightPanel = document.getElementById('right-panel');
    
    updateLeftPanel(newsData.news, newsData.country_info, newsData.urls);
    updateRightPanel(newsData);
    
    
    
}

function updateLeftPanel(news, countryInfo, urls) {
    
    //console.log(countryInfo);
    let countryInfoHtml = `
        <h2>Country: ${countryInfo.name}</h2>
        <p><strong>Capital:</strong> ${countryInfo.capital}<br>
        <strong>Region:</strong> ${countryInfo.region}<br>
        <strong>Subregion:</strong> ${countryInfo.subregion}<br>
        <strong>Population:</strong> ${countryInfo.population.toLocaleString()}
    `;
    if (countryInfo.name == 'China'){
        countryInfoHtml = `
        <h2>Country: ${countryInfo.name}</h2>
        <p><strong>Capital:</strong> Beijing <br>
        <strong>Region:</strong> ${countryInfo.region}<br>
        <strong>Subregion:</strong> ${countryInfo.subregion}<br>
        <strong>Population:</strong> 1,418,847,070`;
    }
    
    //console.log(urls)
    
    let newsHtml = '<br><h2>What\'s happening ? </h2>';
    news.forEach((article, index) => {
        //console.log(urls);
        const url = urls[index];
        const parts = article.split("-"); // Split the article
        const lastPart = parts.pop(); // Extract the last part
        const restOfArticle = parts.join("-"); // Join the rest back
        
        //console.log(lastPart);
        //console.log(urls[index])
        newsHtml += `
            <h4>${restOfArticle} - <a${url ? ` href="${url}" target="_blank" rel="noopener noreferrer"` : ''}>${lastPart}</a></h4>`;
        //newsHtml += `
        //    <h4>${restOfArticle} - <a href="${url}">${lastPart}</a></h4>`; //<a href=${url}> ${article}</a>
          //  <p>${article.description}</p>
        //`;
    });
    //leftPanel.innerHTML = newsHtml;
    leftPanel.innerHTML = countryInfoHtml + newsHtml;
}

function updateRightPanel(newsData) {
    const countryInfo = newsData.country_info;
    //const countryNews = newsData.news;
    const countryPrayers = newsData.prayers;
    const countryReasons = newsData.reasons;


    //console.log(countryInfo.name);
    //const dropdown = document.getElementById('country-dropdown');
    
    
    let prayersHtml = `<h2>What to Pray For ?</h2>
                        <ul>
    `;
    countryPrayers.forEach(prayer => {
        prayersHtml += `
            <li>${prayer}</li>
        `;
    });
    prayersHtml += `</ul>`
    
    let thankfulHtml = `<h2>What to be Grateful For ?</h2>
                        <ul>
    `;
    countryReasons.forEach(reason => {
      thankfulHtml += `
            <li>${reason}</li>
        `;
    });
    thankfulHtml += `</ul>`

    rightPanel.innerHTML = prayersHtml + thankfulHtml
    //rightPanel.innerHTML = countryInfoHtml + prayersHtml + thankfulHtml
    rightPanel.style.display = 'block';
}

function showInfo(country) {
    highlightedCountry = country;
    globe.polygonCapColor(d => d === country ? 'rgba(255, 0, 0, 0.8)' : 'rgba(200, 200, 200, 0.3)');
    
    //fetch(`/api/country/${country.properties.NAME}`)
    const languageCode = navigator.language || navigator.userLanguage;
    const language = new Intl.DisplayNames(['en'], { type: 'language' }).of(languageCode.split('-')[0]);
    //console.log(language);
    countryName = encodeURIComponent(country.properties.NAME)
    fetch(`/api/country/${countryName}/${language}`)
        .then(response => response.json())
        .then(data => {
            const countryInfo = data.country_info;
            const countryNews = data.news;
            const newsUrls = data.urls;
            const countryPrayers = data.prayers;
            const countryReasons = data.reasons;
            
            updateRightPanel(data)
            updateLeftPanel(countryNews,countryInfo,newsUrls);
        });
}

function hideInfo() {
    highlightedCountry = null;
    globe.polygonCapColor(() => 'rgba(200, 200, 200, 0.3)');
    rightPanel.style.display = 'none';
    updateLeftPanel(newsData.news, newsData.country_info, newsData.urls);
}

function init() {

    createGlobe();
    createPanels();
    //*
    // Get the dropdown element
    const dropdown = document.getElementById('country-dropdown');

    fetch('https://raw.githubusercontent.com/vasturiano/globe.gl/master/example/datasets/ne_110m_admin_0_countries.geojson')
        .then(res => res.json())
        .then(({ features }) => {
            countries = features;
        
            countries.sort((a, b) => a.properties.NAME.localeCompare(b.properties.NAME));
        
            //console.log(features[0]);

            // Iterate over each country in the countries array
            countries.forEach(country => {
                
                // Create a new option element
                const option = document.createElement('option');
                
                // Set the value and text content of the option
                option.value = country.properties.NAME;
                option.textContent = country.properties.NAME;
                
                //console.log(country.properties.NAME)
                
                // Append the option to the dropdown
                dropdown.appendChild(option);
            });
            
            //console.log(newsData.country_info.name)
            dropdown.value = newsData.country_info.name;
            
            //console.log(countries)
            globe
                .polygonsData(features)
                .onPolygonHover(hoverD => {
                    globe.polygonAltitude(d => d === hoverD ? 0.12 : 0.06);
                    document.body.style.cursor = hoverD ? 'pointer' : 'default';
                })
                .onPolygonClick(country => {
                    dropdown.value = country.properties.NAME;
                    console.log(country.properties.NAME);
                    const { lat, lng } = d3.geoCentroid(country);
                    showInfo(country);
                    //console.log(lat, lng);
                    globe.pointOfView({ lat: lat, lng: lng }, 2000);
                    //focusOnCountry(lat, lng);
                });
        });

    //const searchInput = document.getElementById('search-input');
    const randomCountryButton = document.getElementById('random-country');

    dropdown.addEventListener('change', (e) => {
        const searchTerm = dropdown.options[dropdown.selectedIndex].text;
        const matchedCountry = countries.find(country => 
            country.properties.NAME.includes(searchTerm)
        );
        //console.log(searchTerm);
        if (matchedCountry) {
            showInfo(matchedCountry);
            const { lat, lng } = d3.geoCentroid(matchedCountry);
            //focusOnCountry(lat, lng);
            globe.pointOfView({ lat: lat, lng: lng }, 2000);
        } else {
            hideInfo();
        }
    });

    randomCountryButton.addEventListener('click', () => {
        const randomCountry = countries[Math.floor(Math.random() * countries.length)];
        showInfo(randomCountry);

        dropdown.value = randomCountry.properties.NAME;
        const { lat, lng } = d3.geoCentroid(randomCountry);
        //focusOnCountry(lat, lng);
        globe.pointOfView({ lat: lat, lng: lng }, 2000);
    });

    animate();
    //*/
    
}

//*
function animate(time) {
  if (typeof TWEEN !== 'undefined') {
      TWEEN.update(time);
  }
  if (autoRotate && globe) {
      const currentRotation = globe.controls().autoRotate;
      globe.controls().autoRotate = true;
      globe.controls().autoRotateSpeed = 1; // Adjust this value to change rotation speed
  }
  requestAnimationFrame(animate);
}
//*/

//*
function focusOnCountry(lat, lng) {
  const distance = 200;
  const distRad = distance / globe.getGlobeRadius();
  const newPos = globe.getCoords(lat, lng, distRad);

  //globe.pointOfView({ lat: lat, lng: lng, altitude: 2 }, 1000);
  
  globe.pointOfView(newPos, 1000);
}
//*/

// Start initialization when the DOM is ready
document.addEventListener('DOMContentLoaded', init);