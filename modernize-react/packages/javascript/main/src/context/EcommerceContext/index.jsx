import React from "react";
import { createContext, useState, useEffect } from 'react';


import useSWR from 'swr';

import { deleteFetcher, getFetcher, postFetcher, putFetcher } from "src/api/globalFetcher";




// Create Context with the specified type
export const ProductContext = createContext({});

// Provider Component
export const ProductProvider = ({ children }) => {
    const [products, setProducts] = useState([]);
    const [searchProduct, setSearchProduct] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('All');
    const [sortBy, setSortBy] = useState('newest');
    const [priceRange, setPriceRange] = useState('All');
    const [selectedGender, setSelectedGender] = useState('All');
    const [selectedColor, setSelectedColor] = useState('All');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [cartItems, setCartItems] = useState(() => {
        // Check if localStorage is defined (for client-side rendering)
        if (typeof window !== 'undefined') {
            const storedCartItems = localStorage.getItem('cartItems');
            return storedCartItems ? JSON.parse(storedCartItems) : [];
        } else {
            return [];
        }
    });

    // Fetch products data from the API 
    const { data: productsData, isLoading: isProductsLoading, error: productsError } = useSWR('/api/data/eCommerce/ProductsData', getFetcher);

    useEffect(() => {
        if (productsData) {
            setProducts(productsData.data);
            setLoading(isProductsLoading);
        } else if (productsError) {
            setError(productsError);
            setLoading(isProductsLoading);
        } else {
            setLoading(isProductsLoading);
        }
    }, [productsData, productsError, isProductsLoading]);

    // Fetch products data from the API 
    const { data: cartsData, isLoading: isCartsLoading, error: cartsError, mutate: cartMutate } = useSWR('/api/eCommerce/carts', getFetcher);

    useEffect(() => {
        if (cartsData) {
            setCartItems(cartsData.data);
            setLoading(isCartsLoading);
        } else if (cartsError) {
            setError(cartsError);
            setLoading(isCartsLoading);
        } else {
            setLoading(isCartsLoading);
        }
    }, [cartsData, cartsError, isCartsLoading])

    // UseEffect to update local storage whenever cartItems changes
    useEffect(() => {
        if (cartItems) {
            localStorage.setItem("cartItems", JSON.stringify(cartItems));
        }
    }, [cartItems]);


    // UseEffect to initialize cartItems from local storage when the component mounts
    useEffect(() => {
        const storedCartItems = localStorage.getItem("cartItems");
        if (storedCartItems) {
            setCartItems(JSON.parse(storedCartItems));
        }
    }, []);

    // Function to filter products based on search, category, price range, gender, and color
    const filterProducts = (product) => {
        const matchesSearch = product.title.toLowerCase().includes(searchProduct.toLowerCase());
        const matchesCategory = selectedCategory === 'All' || product.category.includes(selectedCategory);
        const withinPriceRange = (priceRange === 'All') ||
            (priceRange === '0-50' && product.price <= 50) ||
            (priceRange === '50-100' && product.price > 50 && product.price <= 100) ||
            (priceRange === '100-200' && product.price > 100 && product.price <= 200) ||
            (priceRange === '200-99999' && product.price > 200);
        const matchesGender = selectedGender === 'All' || product.gender === selectedGender;
        const matchesColor = selectedColor === 'All' || product.colors.includes(selectedColor);

        return matchesSearch && matchesCategory && withinPriceRange && matchesGender && matchesColor;
    };

    // Function to sort filtered products based on selected sort option
    const sortProducts = (filteredProducts) => {
        switch (sortBy) {
            case 'newest':
                return filteredProducts.sort((a, b) => new Date(b.created).getTime() - new Date(a.created).getTime());
            case 'priceDesc':
                return filteredProducts.sort((a, b) => b.price - a.price);
            case 'priceAsc':
                return filteredProducts.sort((a, b) => a.price - b.price);
            case 'discount':
                return filteredProducts.sort((a, b) => (b.discount || 0) - (a.discount || 0));
            default:
                return filteredProducts;
        }
    };

    // Function to fetch a product by its ID
    const getProductById = (productId) => {
        const product = products.find(p => p.id === Number(productId));
        return product;
    };

    // Filter and sort products
    const filteredProducts = products.filter(filterProducts);
    const filteredAndSortedProducts = sortProducts(filteredProducts);

    // Function to handle selecting a category
    const selectCategory = (category) => setSelectedCategory(category);

    // Function to update the sort option
    const updateSortBy = (sortOption) => setSortBy(sortOption);

    // Function to update the price range
    const updatePriceRange = (range) => setPriceRange(range);

    // Function to select a gender
    const selectGender = (gender) => setSelectedGender(gender);

    // Function to select a color
    const selectColor = (color) => setSelectedColor(color);

    // Function to search products based on text input
    const searchProducts = (searchText) => setSearchProduct(searchText);

    // Function to add an item to the cart
    const addToCart = async (productId) => {
        try {

            await cartMutate(postFetcher('/api/data/eCommerce/add', { productId }));

        } catch (error) {
            console.error('Error adding product to cart:', error);
        }
    };

    // Function to remove an item from the cart
    const removeFromCart = async (id) => {
        await cartMutate(deleteFetcher('/api/eCommerce/remove-item-carts', { id, action: "Increment" }));
    };


    // Function to increment quantity of a product in the cart
    const incrementQuantity = async (id) => {
        await cartMutate(putFetcher('/api/eCommerce/carts/increment-decrementqty', { id, action: "Increment" }));
    };

    // Function to decrement quantity of a product in the cart
    const decrementQuantity = async (id) => {
        await cartMutate(putFetcher('/api/eCommerce/carts/increment-decrementqty', { id, action: "Decrement" }));
    };

    // Function to delete a product
    const deleteProduct = (productId) => {
        setProducts(products.filter(product => product.id !== productId));
    };

    // Function to delete all products
    const deleteAllProducts = () => {
        setProducts([]);
    };

    //  Function to update a product
    const updateProduct = (productId, updatedProduct) => {
        setProducts(products.map(product => product.id === Number(productId) ? updatedProduct : product));
    };

    const filterReset = () => {
        setSelectedCategory('All');
        setSelectedColor('All');
        setSelectedGender('All');
        setPriceRange('All');
        setSortBy('newest');
    }


    return (
        <ProductContext.Provider
            value={{
                products,
                searchProduct,
                selectedCategory,
                sortBy,
                priceRange,
                selectedGender,
                selectedColor,
                loading,
                error,
                cartItems,
                setProducts,
                setSearchProduct,
                setSelectedCategory,
                setSortBy,
                setPriceRange,
                setSelectedGender,
                setSelectedColor,
                setLoading,
                setCartItems,
                deleteProduct,
                searchProducts,
                updateSortBy,
                updatePriceRange,
                selectCategory,
                selectGender,
                selectColor,
                incrementQuantity,
                decrementQuantity,
                removeFromCart,
                addToCart,
                deleteAllProducts,
                filteredAndSortedProducts,
                filterReset, getProductById,
                updateProduct


            }}
        >
            {children}
        </ProductContext.Provider>
    );
};