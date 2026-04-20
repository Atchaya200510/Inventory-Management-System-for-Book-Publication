/* ---------- LOGIN ROLE ---------- */
function setRole(role) {
    localStorage.setItem("role", role);
}

/* ---------- GLOBAL ---------- */
let allBooks = [];

/* ---------- LOAD BOOKS ---------- */
function loadBooks() {
    const USER_ROLE = localStorage.getItem("role");

    fetch("/api/books")
        .then(res => res.json())
        .then(data => {
            allBooks = data;
            renderBooks(allBooks, USER_ROLE);
        });
}

/* ---------- RENDER BOOKS ---------- */
function renderBooks(books, USER_ROLE) {
    const grid = document.getElementById("booksGrid");
    if (!grid) return;

    grid.innerHTML = "";

    books.forEach(book => {
        const image = book.image_url
            ? `/static/cover/${book.image_url}`
            : `/static/cover/default.jpg`;

        grid.innerHTML += `
            <div class="book-card"
                 onclick="window.location.href='/book/${book.id}'">

                <img src="${image}">
                <div class="book-title">${book.title}</div>
                <div class="book-author">${book.author}</div>
                <div class="book-price">₹${book.price}</div>

                ${
                    USER_ROLE === "staff"
                    ? `
                    <div class="card-actions">
                        <button onclick="event.stopPropagation(); editBook(${book.id})">Edit</button>
                        <button onclick="event.stopPropagation(); deleteBook(${book.id})">Delete</button>
                    </div>
                    `
                    : ""
                }
            </div>
        `;
    });
}

/* ---------- SEARCH + FILTER ---------- */
function applyFilter() {
    const search = document.getElementById("search")
        ? document.getElementById("search").value.toLowerCase()
        : "";

    const category = document.getElementById("category")
        ? document.getElementById("category").value
        : "";

    const filtered = allBooks.filter(book => {
        const matchText =
            book.title.toLowerCase().includes(search) ||
            book.author.toLowerCase().includes(search);

        const matchCategory =
            category === "" || book.category === category;

        return matchText && matchCategory;
    });

    renderBooks(filtered, localStorage.getItem("role"));
}

/* ---------- ADD BOOK ---------- */
function addBook() {
    const formData = new FormData();

    formData.append("title", document.getElementById("title").value);
    formData.append("author", document.getElementById("author").value);
    formData.append("category", document.getElementById("category").value);
    formData.append("quantity", document.getElementById("quantity").value);
    formData.append("price", document.getElementById("price").value);
    formData.append("description", document.getElementById("description").value);

    const imageInput = document.getElementById("image");
    if (imageInput && imageInput.files.length > 0) {
        formData.append("image", imageInput.files[0]);
    }

    fetch("/api/books", {
        method: "POST",
        body: formData
    })
    .then(() => window.location.href = "/staff/view_books");
}

/* ---------- EDIT ---------- */
function editBook(id) {
    fetch(`/api/books/${id}`)
        .then(res => res.json())
        .then(book => {
            localStorage.setItem("editBook", JSON.stringify(book));
            window.location.href = `/staff/edit_book/${id}`;
        });
}

/* ---------- SAVE EDIT ---------- */
function saveBook() {
    const book = JSON.parse(localStorage.getItem("editBook"));

    const formData = new FormData();
    formData.append("title", document.getElementById("title").value);
    formData.append("author", document.getElementById("author").value);
    formData.append("category", document.getElementById("category").value);
    formData.append("price", document.getElementById("price").value);
    formData.append("description", document.getElementById("description").value);

    const imageInput = document.getElementById("image");
    if (imageInput && imageInput.files.length > 0) {
        formData.append("image", imageInput.files[0]);
    }

    fetch(`/api/books/${book.id}`, {
        method: "PUT",
        body: formData
    })
    .then(() => {
        localStorage.removeItem("editBook");
        window.location.href = "/staff/view_books";
    });
}

/* ---------- DELETE ---------- */
function deleteBook(id) {
    if (!confirm("Delete this book?")) return;

    fetch(`/api/books/${id}`, { method: "DELETE" })
        .then(() => loadBooks());
}

/* ---------- UI ---------- */
function toggleFilter() {
    const box = document.getElementById("filterBox");
    if (box) {
        box.style.display = box.style.display === "block" ? "none" : "block";
    }
}

function goBack() {
    const role = localStorage.getItem("role");
    if (role === "admin") window.location.href = "/admin_dashboard";
    else if (role === "staff") window.location.href = "/staff_dashboard";
    else window.location.href = "/";
}

/* ---------- LIVE IMAGE PREVIEW ---------- */
function previewImage(event) {
    const file = event.target.files[0];
    if (!file) return;

    const img = document.getElementById("previewImg");

    const reader = new FileReader();
    reader.onload = () => {
        img.src = reader.result;
        img.style.display = "block";
    };

    reader.readAsDataURL(file);
}
function goBackToBooks() {
    const role = localStorage.getItem("role");

    if (role === "admin") {
        window.location.href = "/admin/view_books";
    } 
    else if (role === "staff") {
        window.location.href = "/staff/view_books";
    } 
    else {
        window.location.href = "/";
    }
}
/* ---------- ON LOAD ---------- */
window.onload = function () {
    if (document.getElementById("booksGrid")) {
        loadBooks();
    }
}
