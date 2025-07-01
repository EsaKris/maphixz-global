<!-- Banner with Logo, Stack, and Designer Info -->
<p align="center">
  <img src="static/images/logo.png" alt="Maphixz Global Logo" width="90" style="border-radius:50%;box-shadow:0 2px 8px #ccc;">
</p>

<h1 align="center">Maphixz Global Ecommerce</h1>

<p align="center">
  <b>Premium Laptops & Accessories Store</b><br>
  <span>
    <img src="https://img.shields.io/badge/Django-4%2B-green?logo=django" alt="Django">
    <img src="https://img.shields.io/badge/TailwindCSS-3%2B-blue?logo=tailwindcss" alt="TailwindCSS">
    <img src="https://img.shields.io/badge/Bootstrap-5-purple?logo=bootstrap" alt="Bootstrap">
    <img src="https://img.shields.io/badge/FontAwesome-6-blueviolet?logo=fontawesome" alt="FontAwesome">
    <img src="https://img.shields.io/badge/SQLite-3-lightgrey?logo=sqlite" alt="SQLite">
  </span>
</p>

<p align="center">
  <a href="https://github.com/EsaKris" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-esa--kris-black?logo=github" alt="GitHub">
  </a>
  <a href="https://www.linkedin.com/in/ekre-christian-18008b299/" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-esa--kris-blue?logo=linkedin" alt="LinkedIn">
  </a>
  <a href="https://www.instagram.com/esakris_/" target="_blank">
    <img src="https://img.shields.io/badge/Instagram-esa.kris-E4405F?logo=instagram&logoColor=white" alt="Instagram">
  </a>
</p>

---

## Features

- **Modern UI**: Responsive, elegant design using Tailwind CSS and Bootstrap.
- **Product Catalog**: Browse, search, and filter premium laptops and accessories by category.
- **Categories**: Laptops, Accessories, Brands, and more.
- **Product Details**: High-quality images, videos, and detailed specifications.
- **Shopping Cart**: Add, update, and remove products from the cart.
- **Checkout**: Secure order placement with multiple payment and delivery options.
- **Custom Admin Portal**: Manage products, categories, orders, and analytics.
- **User Authentication**: Secure login/logout for customers and admin users.
- **Order Management**: Track, update, and manage orders from the admin dashboard.
- **Newsletter Signup**: Collect emails for marketing and updates.
- **SEO Friendly**: Semantic HTML and meta tags for better search engine ranking.

---

## Tech Stack

- **Backend:** Django 4+/5+
- **Frontend:** Tailwind CSS, Bootstrap, Font Awesome, Google Fonts
- **Database:** SQLite (default), easily switchable to PostgreSQL/MySQL
- **Media:** Django static and media files for product images and videos

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/maphixz-global.git
cd maphixz-global
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Create a Superuser

```bash
python manage.py createsuperuser
```

### 6. Collect Static Files

```bash
python manage.py collectstatic
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to view the site.

---

## Initial Data: Add Default Categories

To add the main product categories, run:

```python
python manage.py shell
```
```python
from store.models import Category
from django.utils.text import slugify

category_names = [
    "Laptops",
    "Accessories",
    "Brands"
]

for name in category_names:
    Category.objects.get_or_create(
        name=name,
        defaults={'slug': slugify(name)}
    )
```

---

## Project Structure

```
maphixz-global/
├── manage.py
├── requirements.txt
├── store/
│   ├── admin.py
│   ├── admin_views.py
│   ├── models.py
│   ├── views.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── store/
│   │   │   ├── home.html
│   │   │   ├── product_list.html
│   │   │   ├── contact.html
│   │   ├── admin/
│   │   │   ├── products.html
│   │   │   ├── add_product.html
│   │   │   ├── edit_product.html
│   │   │   ├── dashboard.html
│   │   │   └── ...
│   └── ...
├── static/
│   ├── css/
│   ├── images/
│   ├── js/
│   └── ...
└── ...
```

---

## Customization

- **Branding:** Update `base.html` and static assets for your brand.
- **Categories:** Add or edit categories in the Django admin or via shell.
- **Products:** Add laptops and accessories with images and videos via the admin portal.
- **Contact Info:** Update footer and contact page with your business details.

---

## Admin Portal

- Visit `/admin/` for Django's default admin.
- Visit `/maphixz-admin/` (or your custom admin URL) for the custom admin dashboard.
- Only staff or superusers can access admin features.

---

## Deployment

- Set `DEBUG = False` and configure `ALLOWED_HOSTS` in `settings.py`.
- Use a production-ready database (e.g., PostgreSQL).
- Serve static and media files with a web server (e.g., Nginx).
- Use HTTPS in production.

---

## License

This project is licensed under the MIT License.

---

## Credits

- [Django](https://www.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/)
- [Google Fonts](https://fonts.google.com/)

---

## Contact

For support or business inquiries, email: **hello@maphixzglobal.com**

---

<p align="center">
<a href="https://github.com/EsaKris" target="_blank"><img src="https://img.shields.io/badge/GitHub-esa--kris-black?logo=github" alt="GitHub"></a>
  <a href="https://www.linkedin.com/in/esa-kris" target="_blank"><img src="https://img.shields.io/badge/LinkedIn-Esa_Kris-0077B5?logo=linkedin&logoColor=white" alt="LinkedIn"></a>
  <a href="https://www.instagram.com/esakris_/" target="_blank"><img src="https://img.shields.io/badge/Instagram-esa.kris-E4405F?logo=instagram&logoColor=white" alt="Instagram"></a>
</p>