// ============================================================
// SHOPKART - COMPLETE JAVASCRIPT
// ============================================================


// ============================================================
// 1. GET CURRENT USER ID
// ============================================================

function getCurrentUserId() {

    const userElement =
        document.getElementById("shopkart-user-id");

    if (userElement) {

        const userId =
            userElement.getAttribute("data-user-id");

        if (
            userId &&
            userId !== "None" &&
            userId !== "null" &&
            userId !== "undefined" &&
            userId !== ""
        ) {

            return String(userId);

        }

    }

    return "guest";
}


// ============================================================
// 2. GET USER-SPECIFIC CART KEY
// ============================================================

function getCartKey() {

    const userId =
        getCurrentUserId();

    return "shopkart_cart_user_" + userId;
}


// ============================================================
// 3. GET CART
// ============================================================

function getCart() {

    const cartKey =
        getCartKey();

    try {

        const storedCart =
            localStorage.getItem(cartKey);

        if (!storedCart) {

            return [];

        }


        const cart =
            JSON.parse(storedCart);


        if (!Array.isArray(cart)) {

            return [];

        }


        return cart;

    }

    catch (error) {

        console.error(
            "Error loading cart:",
            error
        );

        return [];

    }
}


// ============================================================
// 4. SAVE CART
// ============================================================

function saveCart(cart) {

    const cartKey =
        getCartKey();


    try {

        localStorage.setItem(
            cartKey,
            JSON.stringify(cart)
        );


        updateCartCount();

    }

    catch (error) {

        console.error(
            "Error saving cart:",
            error
        );

    }
}


// ============================================================
// 5. UPDATE CART COUNT
// ============================================================

function updateCartCount() {

    const cart =
        getCart();


    let totalQuantity = 0;


    cart.forEach(function(product) {

        totalQuantity +=
            Number(
                product.quantity || 0
            );

    });


    const cartCountElements =
        document.querySelectorAll(
            ".cart-count"
        );


    cartCountElements.forEach(
        function(element) {

            element.textContent =
                totalQuantity;

        }
    );

}


// ============================================================
// 6. ADD TO CART
// ============================================================

function addToCart(
    productId,
    productName,
    productPrice,
    productStock,
    productImage
) {

    const cart =
        getCart();


    const id =
        Number(productId);

    const price =
        Number(productPrice);

    const stock =
        Number(productStock);


    // --------------------------------------------------------
    // STOCK CHECK
    // --------------------------------------------------------

    if (stock <= 0) {

        alert(
            "This product is out of stock."
        );

        return;

    }


    // --------------------------------------------------------
    // FIND EXISTING PRODUCT
    // --------------------------------------------------------

    const existingProduct =
        cart.find(function(product) {

            return Number(product.id)
                === id;

        });


    // --------------------------------------------------------
    // PRODUCT ALREADY IN CART
    // --------------------------------------------------------

    if (existingProduct) {

        const currentQuantity =
            Number(
                existingProduct.quantity
            );


        if (
            currentQuantity >= stock
        ) {

            alert(
                "You cannot add more than available stock."
            );

            return;

        }


        existingProduct.quantity =
            currentQuantity + 1;


        existingProduct.price =
            price;


        existingProduct.stock =
            stock;


        if (productImage) {

            existingProduct.image =
                productImage;

        }

    }


    // --------------------------------------------------------
    // NEW PRODUCT
    // --------------------------------------------------------

    else {

        cart.push({

            id: id,

            name: productName,

            price: price,

            quantity: 1,

            stock: stock,

            image: productImage || ""

        });

    }


    // --------------------------------------------------------
    // SAVE
    // --------------------------------------------------------

    saveCart(cart);

    updateCartCount();


    // --------------------------------------------------------
    // MESSAGE
    // --------------------------------------------------------

    alert(
        productName +
        " added to cart!"
    );

}


// ============================================================
// 7. ADD PRODUCT FROM PRODUCTS PAGE
// ============================================================

function addProductToCart(button) {

    if (!button) {

        return;

    }


    const productId =
        button.dataset.id;

    const productName =
        button.dataset.name;

    const productPrice =
        button.dataset.price;

    const productStock =
        button.dataset.stock;

    const productImage =
        button.dataset.image;


    addToCart(
        productId,
        productName,
        productPrice,
        productStock,
        productImage
    );

}


// ============================================================
// 8. ADD PRODUCT FROM HOME PAGE
// ============================================================

function addHomeProductToCart(button) {

    if (!button) {

        return;

    }


    const productId =
        button.dataset.id;

    const productName =
        button.dataset.name;

    const productPrice =
        button.dataset.price;

    const productStock =
        button.dataset.stock;

    const productImage =
        button.dataset.image;


    addToCart(
        productId,
        productName,
        productPrice,
        productStock,
        productImage
    );

}


// ============================================================
// 9. GENERIC SHOPKART ADD TO CART
// ============================================================

function shopKartAddToCart(
    productId,
    productName,
    productPrice,
    productStock,
    productImage
) {

    addToCart(
        productId,
        productName,
        productPrice,
        productStock,
        productImage
    );

}


// ============================================================
// 10. INCREASE QUANTITY
// ============================================================

function increaseQuantity(productId) {

    const cart =
        getCart();


    const product =
        cart.find(function(item) {

            return Number(item.id)
                === Number(productId);

        });


    if (!product) {

        return;

    }


    const quantity =
        Number(product.quantity);


    const stock =
        Number(product.stock);


    if (
        quantity >= stock
    ) {

        alert(
            "You cannot add more than available stock."
        );

        return;

    }


    product.quantity =
        quantity + 1;


    saveCart(cart);

    displayCart();

}


// ============================================================
// 11. DECREASE QUANTITY
// ============================================================

function decreaseQuantity(productId) {

    const cart =
        getCart();


    const product =
        cart.find(function(item) {

            return Number(item.id)
                === Number(productId);

        });


    if (!product) {

        return;

    }


    const quantity =
        Number(product.quantity);


    // --------------------------------------------------------
    // DECREASE
    // --------------------------------------------------------

    if (quantity > 1) {

        product.quantity =
            quantity - 1;

    }


    // --------------------------------------------------------
    // REMOVE IF QUANTITY = 1
    // --------------------------------------------------------

    else {

        const index =
            cart.findIndex(function(item) {

                return Number(item.id)
                    === Number(productId);

            });


        if (index !== -1) {

            cart.splice(
                index,
                1
            );

        }

    }


    saveCart(cart);

    displayCart();

}


// ============================================================
// 12. REMOVE PRODUCT
// ============================================================

function removeFromCart(productId) {

    let cart =
        getCart();


    const product =
        cart.find(function(item) {

            return Number(item.id)
                === Number(productId);

        });


    if (!product) {

        return;

    }


    const confirmed =
        confirm(
            "Remove " +
            product.name +
            " from cart?"
        );


    if (!confirmed) {

        return;

    }


    cart =
        cart.filter(function(item) {

            return Number(item.id)
                !== Number(productId);

        });


    saveCart(cart);

    displayCart();

}


// ============================================================
// 13. CLEAR CURRENT USER CART
// ============================================================

function clearCart() {

    const confirmed =
        confirm(
            "Are you sure you want to clear your cart?"
        );


    if (!confirmed) {

        return;

    }


    const cartKey =
        getCartKey();


    localStorage.removeItem(
        cartKey
    );


    updateCartCount();

    displayCart();

}


// ============================================================
// 14. DISPLAY CART
// ============================================================

function displayCart() {

    const cartContainer =
        document.getElementById(
            "cart-items"
        );


    // Not on cart page
    if (!cartContainer) {

        return;

    }


    const cart =
        getCart();


    // ========================================================
    // EMPTY CART
    // ========================================================

    if (cart.length === 0) {

        cartContainer.innerHTML = `

            <div class="empty-cart">

                <div class="empty-cart-icon">
                    🛒
                </div>

                <h2>
                    Your Cart is Empty
                </h2>

                <p>
                    Add some products to your cart.
                </p>

                <a
                    href="/products"
                    class="continue-shopping"
                >
                    Continue Shopping
                </a>

            </div>

        `;


        updateCartSummary();

        updateCartCount();

        return;

    }


    // ========================================================
    // CART HTML
    // ========================================================

    let html = "";


    cart.forEach(function(product) {

        const id =
            Number(product.id);

        const name =
            product.name || "Product";

        const price =
            Number(product.price || 0);

        const quantity =
            Number(product.quantity || 0);

        const stock =
            Number(product.stock || 0);

        const image =
            product.image || "";


        const itemTotal =
            price * quantity;


        let imageHTML = "";


        if (image) {

            imageHTML = `

                <img
                    src="/static/images/${encodeURIComponent(image)}"
                    alt="${escapeHTML(name)}"
                    class="cart-product-image"
                    onerror="this.style.display='none';"
                >

            `;

        }

        else {

            imageHTML = `

                <div class="no-cart-image">
                    🛍️
                </div>

            `;

        }


        html += `

            <div class="cart-item">

                <div class="cart-image-box">

                    ${imageHTML}

                </div>


                <div class="cart-product-info">

                    <h3>
                        ${escapeHTML(name)}
                    </h3>


                    <p class="cart-price">

                        ₹${price.toFixed(2)}

                    </p>


                    <p class="cart-stock">

                        Available Stock:
                        ${stock}

                    </p>

                </div>


                <div class="quantity-control">


                    <button
                        type="button"
                        onclick="decreaseQuantity(${id})"
                    >
                        −
                    </button>


                    <span>
                        ${quantity}
                    </span>


                    <button
                        type="button"
                        onclick="increaseQuantity(${id})"
                    >
                        +
                    </button>


                </div>


                <div class="cart-item-total">

                    ₹${itemTotal.toFixed(2)}

                </div>


                <button
                    type="button"
                    class="remove-btn"
                    onclick="removeFromCart(${id})"
                >
                    🗑️ Remove
                </button>


            </div>

        `;

    });


    cartContainer.innerHTML =
        html;


    updateCartSummary();

    updateCartCount();

}


// ============================================================
// 15. UPDATE CART SUMMARY
// ============================================================

function updateCartSummary() {

    const cart =
        getCart();


    let subtotal = 0;

    let totalItems = 0;


    cart.forEach(function(product) {

        const price =
            Number(
                product.price || 0
            );

        const quantity =
            Number(
                product.quantity || 0
            );


        subtotal +=
            price * quantity;


        totalItems +=
            quantity;

    });


    // --------------------------------------------------------
    // ITEMS
    // --------------------------------------------------------

    const itemsElement =
        document.getElementById(
            "cart-total-items"
        );


    if (itemsElement) {

        itemsElement.textContent =
            totalItems;

    }


    // --------------------------------------------------------
    // SUBTOTAL
    // --------------------------------------------------------

    const subtotalElement =
        document.getElementById(
            "cart-subtotal"
        );


    if (subtotalElement) {

        subtotalElement.textContent =
            "₹" +
            subtotal.toFixed(2);

    }


    // --------------------------------------------------------
    // TOTAL
    // --------------------------------------------------------

    const totalElement =
        document.getElementById(
            "cart-total"
        );


    if (totalElement) {

        totalElement.textContent =
            "₹" +
            subtotal.toFixed(2);

    }


    // --------------------------------------------------------
    // CHECKOUT TOTAL
    // --------------------------------------------------------

    const checkoutTotal =
        document.getElementById(
            "checkout-total"
        );


    if (checkoutTotal) {

        checkoutTotal.value =
            subtotal.toFixed(2);

    }


    // --------------------------------------------------------
    // CHECKOUT BUTTON
    // --------------------------------------------------------

    const checkoutButton =
        document.getElementById(
            "checkout-button"
        );


    if (checkoutButton) {

        if (cart.length === 0) {

            checkoutButton.style.opacity =
                "0.5";

            checkoutButton.style.pointerEvents =
                "none";

        }

        else {

            checkoutButton.style.opacity =
                "1";

            checkoutButton.style.pointerEvents =
                "auto";

        }

    }

}


// ============================================================
// 16. GET CART TOTAL
// ============================================================

function getCartTotal() {

    const cart =
        getCart();


    let total = 0;


    cart.forEach(function(product) {

        total +=
            Number(
                product.price || 0
            )
            *
            Number(
                product.quantity || 0
            );

    });


    return total;

}


// ============================================================
// 17. GET TOTAL ITEMS
// ============================================================

function getCartItemCount() {

    const cart =
        getCart();


    let count = 0;


    cart.forEach(function(product) {

        count +=
            Number(
                product.quantity || 0
            );

    });


    return count;

}


// ============================================================
// 18. ESCAPE HTML
// ============================================================

function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


// ============================================================
// 19. SEARCH PRODUCTS
// ============================================================

function searchProducts() {

    const input =
        document.getElementById(
            "searchInput"
        );


    if (!input) {

        return;

    }


    const searchValue =
        input.value
            .toLowerCase()
            .trim();


    const cards =
        document.querySelectorAll(
            ".product-card"
        );


    cards.forEach(function(card) {

        const text =
            card.textContent
                .toLowerCase();


        if (
            text.includes(
                searchValue
            )
        ) {

            card.style.display =
                "";

        }

        else {

            card.style.display =
                "none";

        }

    });

}


// ============================================================
// 20. CATEGORY FILTER
// ============================================================

function filterCategory(category) {

    const cards =
        document.querySelectorAll(
            ".product-card"
        );


    const selectedCategory =
        String(category)
            .trim()
            .toLowerCase();


    cards.forEach(function(card) {

        const productCategory =
            String(
                card.dataset.category || ""
            )
            .trim()
            .toLowerCase();


        if (
            selectedCategory === "all"
            ||
            productCategory === selectedCategory
        ) {

            card.style.display =
                "";

        }

        else {

            card.style.display =
                "none";

        }

    });


    // Scroll to products section

    const productsGrid =
        document.querySelector(
            ".products-grid"
        );


    if (productsGrid) {

        productsGrid.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }

}


// ============================================================
// 21. CHECK CURRENT USER
// ============================================================

function showCartDebugInfo() {

    console.log(
        "================================"
    );

    console.log(
        "SHOPKART CART DEBUG"
    );

    console.log(
        "User ID:",
        getCurrentUserId()
    );

    console.log(
        "Cart Key:",
        getCartKey()
    );

    console.log(
        "Cart:",
        getCart()
    );

    console.log(
        "Cart Count:",
        getCartItemCount()
    );

    console.log(
        "Cart Total:",
        getCartTotal()
    );

    console.log(
        "================================"
    );

}


// ============================================================
// 22. PAGE LOAD
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        updateCartCount();

        displayCart();

        updateCartSummary();

        showCartDebugInfo();

    }
);