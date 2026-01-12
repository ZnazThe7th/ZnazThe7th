const API_BASE = "http://localhost:8000";

const serviceSelect = document.querySelector("#service-select");
const bookingForm = document.querySelector("#booking-form");
const bookingStatus = document.querySelector("#booking-status");
const appointmentsList = document.querySelector("#appointments");
const clientsWrap = document.querySelector("#clients");

const formatDateTime = (value) => {
  const date = new Date(value);
  return date.toLocaleString();
};

const fetchJson = async (path, options = {}) => {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Request failed");
  }
  return response.json();
};

const loadServices = async () => {
  const services = await fetchJson("/services");
  serviceSelect.innerHTML = '<option value="">Select a service</option>';
  services.forEach((service) => {
    const option = document.createElement("option");
    option.value = service.id;
    option.textContent = `${service.name} (${service.duration_minutes} min)`;
    serviceSelect.appendChild(option);
  });
};

const loadAppointments = async () => {
  const appointments = await fetchJson("/appointments");
  appointmentsList.innerHTML = "";
  appointments.forEach((appointment) => {
    const item = document.createElement("li");
    item.innerHTML = `
      <strong>${appointment.client_name}</strong><br />
      ${appointment.service_name} · ${formatDateTime(appointment.start_time)}
    `;
    appointmentsList.appendChild(item);
  });
};

const loadClients = async () => {
  const clients = await fetchJson("/clients");
  clientsWrap.innerHTML = "";
  clients.forEach((client) => {
    const pill = document.createElement("span");
    pill.className = "pill";
    pill.textContent = client.full_name;
    clientsWrap.appendChild(pill);
  });
};

const seedServices = async () => {
  const services = await fetchJson("/services");
  if (services.length) {
    return;
  }
  await fetchJson("/services", {
    method: "POST",
    body: JSON.stringify({
      name: "Signature Cut",
      duration_minutes: 45,
      price_cents: 4500,
    }),
  });
  await fetchJson("/services", {
    method: "POST",
    body: JSON.stringify({
      name: "Beard Refresh",
      duration_minutes: 30,
      price_cents: 3000,
    }),
  });
};

bookingForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  bookingStatus.textContent = "";

  const formData = new FormData(bookingForm);
  const clientPayload = {
    full_name: formData.get("full_name"),
    phone: formData.get("phone"),
    email: formData.get("email") || null,
    notes: null,
  };

  try {
    const client = await fetchJson("/clients", {
      method: "POST",
      body: JSON.stringify(clientPayload),
    });

    const appointmentPayload = {
      service_id: Number(formData.get("service_id")),
      client_id: client.id,
      start_time: formData.get("start_time"),
      end_time: formData.get("end_time"),
    };

    await fetchJson("/appointments", {
      method: "POST",
      body: JSON.stringify(appointmentPayload),
    });

    bookingStatus.textContent = "Booked successfully and synced.";
    bookingForm.reset();
    await loadAppointments();
    await loadClients();
  } catch (error) {
    bookingStatus.textContent = `Error: ${error.message}`;
  }
});

const init = async () => {
  try {
    await seedServices();
    await loadServices();
    await loadAppointments();
    await loadClients();
  } catch (error) {
    bookingStatus.textContent = "Unable to reach backend API.";
  }
};

init();
