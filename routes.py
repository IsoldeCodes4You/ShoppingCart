@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})

    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))

        if product:
            subtotal = product.price * quantity
            total += subtotal

            items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

    return render_template('cart.html', items=items, total=total)

@app.route('/product/addToCart/<int:product_id>')
def addtocart(product_id):

    product = Product.query.get(product_id)

    if not product:
        return "Product not found"

    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    product_id_str = str(product_id)

    current_quantity = cart.get(product_id_str, 0)

    if current_quantity + 1 > product.quantity:
        return "Not enough stock available"

    # add item
    cart[product_id_str] = current_quantity + 1

    session['cart'] = cart
    session.modified = True

    return redirect(url_for('products'))

@app.route('/cart/remove/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})

    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]

    session['cart'] = cart
    session.modified = True

    return redirect(url_for('products'))

@app.route('/checkout')
@login_required
def checkout():
    cart = session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

    return render_template('checkout.html', items=items, total=total)

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    cart = session.get('cart', {})
    
    # Validate stock and process order
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if not product or product.quantity < quantity:
            # Not enough stock, redirect back to checkout with error
            return redirect(url_for('checkout'))
        
        # Reduce stock
        product.quantity -= quantity
    
    # Commit all changes
    db.session.commit()
    
    # Clear the cart
    session['cart'] = {}
    session.modified = True
    
    return render_template('order_success.html')
