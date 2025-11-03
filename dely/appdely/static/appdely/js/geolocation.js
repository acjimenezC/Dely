/* Geolocalización Dely - Obtener ubicación del usuario automáticamente */

document.addEventListener('DOMContentLoaded', function() {
    // Verificar si navegador soporta Geolocation
    if ('geolocation' in navigator) {
        // Recuperar ubicación guardada en localStorage
        const storedLocation = localStorage.getItem('dely_user_location');
        
        if (!storedLocation) {
            // Pedir permiso al usuario
            navigator.geolocation.getCurrentPosition(
                success,
                error,
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000 // 5 minutos
                }
            );
        } else {
            // Usar ubicación guardada
            const location = JSON.parse(storedLocation);
            updateUI(location);
        }
    }
});

function success(position) {
    const coords = position.coords;
    const location = {
        latitude: coords.latitude,
        longitude: coords.longitude,
        accuracy: coords.accuracy,
        timestamp: new Date().getTime()
    };
    
    // Guardar en localStorage
    localStorage.setItem('dely_user_location', JSON.stringify(location));
    
    // Actualizar UI y hacer fetch de datos cercanos
    updateUI(location);
    fetchNearbyBusinesses(location);
}

function error(err) {
    console.log(`Error en geolocalización: ${err.message}`);
    
    // Fallback: usar ubicación por defecto de Medellín
    const defaultLocation = {
        latitude: 6.2442,
        longitude: -75.5812,
        address: 'Centro, Medellín',
        isDefault: true
    };
    updateUI(defaultLocation);
}

// Función para convertir coordenadas a dirección (Geocoding inverso)
async function getAddressFromCoords(lat, lon) {
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=18&addressdetails=1`);
        const data = await response.json();
        
        // Extraer información útil de la dirección
        const address = data.address;
        let displayAddress = '';
        
        // Construir dirección: Carrera/Calle + Número
        if (address.road) {
            displayAddress = address.road;
        }
        if (address.house_number) {
            displayAddress += ' #' + address.house_number;
        }
        if (address.neighbourhood) {
            displayAddress += ', ' + address.neighbourhood;
        }
        if (address.city) {
            displayAddress += ', ' + address.city;
        }
        
        return displayAddress || data.address.country;
    } catch (error) {
        console.log('Error al obtener dirección:', error);
        return 'Ubicación desconocida';
    }
}

function updateUI(location) {
    // Crear o buscar el contenedor en la sidebar
    let badge = document.getElementById('geolocation-badge');
    
    if (!badge) {
        // Buscar la sidebar (aside.col-md-3) y crear el badge dentro
        const aside = document.querySelector('aside.col-md-3');
        if (aside) {
            badge = document.createElement('div');
            badge.id = 'geolocation-badge';
            badge.className = 'bg-white rounded shadow-sm p-3 mb-4';
            // Insertarlo después de todos los filtros existentes
            aside.appendChild(badge);
        }
    }
    
    if (badge) {
        const accuracyText = location.accuracy ? `±${location.accuracy.toFixed(0)}m de precisión` : 'Ubicación por defecto';
        const statusText = location.isDefault ? '(Por defecto - Medellín)' : '';
        
        // Mostrar loading mientras se obtiene la dirección
        badge.innerHTML = `
            <div style="font-size: 0.9rem;">
                <div class="d-flex align-items-center gap-2 mb-2">
                    <i class="fas fa-map-pin text-danger" style="font-size: 1.3rem;"></i>
                    <div>
                        <strong class="text-danger d-block">Tu ubicación</strong>
                        <small class="text-muted">${accuracyText}</small>
                    </div>
                </div>
                <div class="bg-light rounded p-2 mb-2" style="font-size: 0.85rem;">
                    <small class="text-muted d-block">
                        ${location.address ? location.address : '<em>Obteniendo dirección...</em>'}
                        ${statusText ? '<br><em class="text-muted">' + statusText + '</em>' : ''}
                    </small>
                </div>
                <button class="btn btn-sm btn-danger w-100" onclick="refreshLocation()">
                    <i class="fas fa-sync-alt me-1"></i>Actualizar ubicación
                </button>
            </div>
        `;
        
        // Si no tiene dirección guardada, obtenerla
        if (!location.address) {
            getAddressFromCoords(location.latitude, location.longitude).then(address => {
                location.address = address;
                // Guardar dirección en localStorage
                localStorage.setItem('dely_user_location', JSON.stringify(location));
                // Actualizar UI nuevamente con la dirección
                updateUI(location);
            });
        }
    }
}

function fetchNearbyBusinesses(location) {
    // Enviar ubicación al servidor para filtrar negocios cercanos
    fetch('/api/nearby-businesses/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            latitude: location.latitude,
            longitude: location.longitude
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Negocios cercanos:', data);
        // Aquí podría actualizar la UI con los negocios cercanos
        // (Lo haremos en la vista Django)
    })
    .catch(error => console.log('Error:', error));
}

// Helper para obtener CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Función para obtener ubicación guardada desde Python/Django
function getUserLocation() {
    const storedLocation = localStorage.getItem('dely_user_location');
    return storedLocation ? JSON.parse(storedLocation) : null;
}

// Función para actualizar ubicación manualmente
function refreshLocation() {
    localStorage.removeItem('dely_user_location');
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            success,
            error,
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0 // Forzar nueva ubicación
            }
        );
    }
}
