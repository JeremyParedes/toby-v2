async function cargarPrestamos() {

    const respuesta = await fetch('/prestamos')

    const prestamos = await respuesta.json()

    const tabla = document.getElementById('tabla')

    tabla.innerHTML = ""

    prestamos.forEach(p => {

        tabla.innerHTML += `
            <tr>
                <td>${p.id}</td>
                <td>${p.cliente}</td>
                <td>S/${p.monto}</td>
                <td>${p.interes}%</td>
                <td>S/${p.deuda + p.pagado}</td>
                <td>S/${p.deuda}</td>
                <td>S/${p.pagado}</td>
                <td>${p.estado}</td>

                <td>

                    <button onclick="mostrarFormularioPago(${p.id})">
                        Pagar
                    </button>

                    <button onclick="verPagos(${p.id})">
                        Ver Pagos
                    </button>

                    <button onclick="eliminarPrestamo(${p.id})">
                        Eliminar
                    </button>

                    <div id="pago-${p.id}" class="formPago"></div>
                    <div id="historial-${p.id}"></div>

                </td>
            </tr>
        `
    })
}

document
.getElementById('formPrestamo')
.addEventListener('submit', async function(e){

    e.preventDefault()

    const cliente = document.getElementById('cliente').value
    const monto = document.getElementById('monto').value
    const interes = document.getElementById('interes').value

    const datos = {
        cliente: cliente,
        monto: Number(monto),
        interes: Number(interes),
        estado: "Activo"
    }

    const respuesta = await fetch('/prestamos', {

        method: 'POST',

        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify(datos)
    })

    if(respuesta.ok){

        document
        .getElementById('formPrestamo')
        .reset()

        cargarPrestamos()
        cargarDashboard()

    }else{

        alert('Error al agregar préstamo')
    }
})

function mostrarFormularioPago(id){

    const contenedor =
        document.getElementById(`pago-${id}`)

    contenedor.innerHTML = `

        <br>

        <input type="number"
               id="monto-${id}"
               placeholder="Monto">

        <input type="date"
               id="fecha-${id}">

        <button onclick="guardarPago(${id})">
            Guardar
        </button>
    `
}

cargarPrestamos()
cargarDashboard()

async function verPagos(id){

    const contenedor =
        document.getElementById(`historial-${id}`)

    // SI YA ESTÁ ABIERTO → CERRAR
    if(contenedor.innerHTML !== ""){
        contenedor.innerHTML = ""
        return
    }

    const respuesta =
        await fetch(`/prestamos/${id}/pagos`)

    const pagos = await respuesta.json()

    let html = `
        <div class="historialCaja">

        <h3>Historial de Pagos</h3>

        <table class="tablaHistorial">

            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Monto</th>
                </tr>
            </thead>

            <tbody>
    `

    pagos.forEach(p => {

        html += `
            <tr>
                <td>${p.fecha_pago}</td>
                <td>S/${p.monto_pago}</td>
            </tr>
        `
    })

    html += `
            </tbody>
        </table>
        </div>
    `

    contenedor.innerHTML = html
}

async function cargarDashboard(){

    const respuesta =
        await fetch('/dashboard')

    const datos =
        await respuesta.json()

    document
    .getElementById('clientes')
    .innerText = datos.clientes

    document
    .getElementById('prestado')
    .innerText = `S/${datos.prestado}`

    document
    .getElementById('pagado')
    .innerText = `S/${datos.pagado}`

    document
    .getElementById('pendiente')
    .innerText = `S/${datos.pendiente}`

    document
    .getElementById('ganancia')
    .innerText = `S/${datos.ganancia}`
}

async function guardarPago(id){

    const monto =
        document.getElementById(`monto-${id}`).value

    let fecha =
    document.getElementById(`fecha-${id}`).value

    const partes = fecha.split("-")

    fecha =
        `${partes[2]}/${partes[1]}/${partes[0]}`

    const respuesta = await fetch(
        `/prestamos/${id}/pagar`,
    {
        method:'PUT',

        headers:{
            'Content-Type':'application/json'
        },

        body: JSON.stringify({
            monto_pago:Number(monto),
            fecha_pago:fecha
        })
    })

    if(respuesta.ok){

        alert("Pago registrado")

        cargarPrestamos()
        cargarDashboard()

    }else{

        alert("Error")
    }
}
async function eliminarPrestamo(id){

    const confirmar =
        confirm("¿Eliminar préstamo?")

    if(!confirmar) return

    const respuesta = await fetch(
        `/prestamos/${id}`,
    {
        method:'DELETE'
    })

    if(respuesta.ok){

        cargarPrestamos()
        cargarDashboard()

        document
        .getElementById('tablaPagos')
        .innerHTML = ""

    }else{

        alert("Error eliminando")
    }
}
function buscarCliente(){

    const input =
        document.getElementById('busqueda')

    const filtro =
        input.value.toLowerCase()

    const filas =
        document.querySelectorAll('#tabla tr')

    filas.forEach(fila => {

        const texto =
            fila.innerText.toLowerCase()

        if(texto.includes(filtro)){

            fila.style.display = ""

        }else{

            fila.style.display = "none"
        }
    })
}