import { sub } from 'date-fns';
import { Chance } from 'chance';
import s1 from 'src/assets/images/products/s1.jpg';
import s2 from 'src/assets/images/products/s2.jpg';
import s3 from 'src/assets/images/products/s3.jpg';
import s4 from 'src/assets/images/products/s4.jpg';
import s5 from 'src/assets/images/products/s5.jpg';
import s6 from 'src/assets/images/products/s6.jpg';
import s7 from 'src/assets/images/products/s7.jpg';
import s8 from 'src/assets/images/products/s8.jpg';
import s9 from 'src/assets/images/products/s9.jpg';
import s10 from 'src/assets/images/products/s10.jpg';
import s11 from 'src/assets/images/products/s11.jpg';
import s12 from 'src/assets/images/products/s12.jpg';
import { http, HttpResponse } from 'msw';

const chance = new Chance();

const ProductsData = [
  {
    title: 'How Innovation Works',
    price: 275,
    discount: 25,
    related: false,
    salesPrice: 350,
    category: ['books'],
    gender: 'Men',
    rating: 3,
    stock: true,
    qty: 1,
    colors: ['#1890FF'],
    photo: s1,
    id: 1,
    created: sub(new Date(), { days: 8, hours: 6, minutes: 20 }),
    description: chance.paragraph({ sentences: 2 }),
  },
  {
    title: 'Psalms Book for Growth',
    price: 89,
    discount: 10,
    related: true,
    salesPrice: 99,
    category: ['books'],
    gender: 'Women',
    rating: 3,
    stock: false,
    qty: 1,
    colors: ['#1890FF', '#94D82D', '#FF4842'],
    photo: s2,
    id: 2,
    created: sub(new Date(), { days: 10, hours: 8, minutes: 69 }),
    description: chance.paragraph({ sentences: 2 }),
  },
  {
    title: 'The Psychology of Money',
    price: 125,
    discount: 12,
    related: false,
    salesPrice: 137,
    category: ['fashion', 'books'],
    gender: 'Kids',
    rating: 3,
    stock: true,
    qty: 1,
    colors: ['#FF4842', '#1890FF', '#94D82D'],
    photo: s3,
    id: 3,
    created: sub(new Date(), { days: 8, hours: 6, minutes: 20 }),
    description: chance.paragraph({ sentences: 2 }),
  },
  {
    title: 'Boat Headphone',
    price: 50,
    discount: 15,
    related: true,
    salesPrice: 65,
    category: ['electronics'],
    gender: 'Men',
    rating: 3,
    stock: true,
    qty: 1,
    colors: ['#1890FF', '#94D82D', '#FFC107'],
    photo: s4,
    id: 4,
    created: sub(new Date(), { days: 4, hours: 9, minutes: 40 }),
    description: chance.paragraph({ sentences: 2 }),
  },
  {
    title: 'MacBook Air Pro',
    price: 650,
    discount: 250,
    related: true,
    salesPrice: 900,
    category: ['fashion', 'electronics'],
    gender: 'Women',
    rating: 3,
    stock: false,
    qty: 1,
    colors: ['#00AB55', '#000000'],
    photo: s5,
    id: 5,
    created: sub(new Date(), { days: 2, hours: 5, minutes: 50 }),
    description: chance.paragraph({ sentences: 2 }),
  },
  {
    title: 'Gaming Console',
    price: 25,
    discount: 6,
    related: true,
    salesPrice: 31,
    category: ['electronics'],
    gender: 'Men',
    rating: 3,
    stock: true,
    qty: 1,
    colors: ['#FFC0CB', '#FF4842'],
    photo: s6,
    id: 6,
    created: sub(new Date(), { days: 2, hours: 9, minutes: 45 }),
    description: chance.paragraph({ sentences: 2 }),
  },
  {
    title: 'Red Valvet Dress',
    price: 150,
    discount: 50,
    related: false,
    salesPrice: 200,
    category: ['fashion'],
    gender: 'Women',
    rating: 3,
    stock: true,
    qty: 1,
    colors: ['#FF4842', '#1890FF', '#94D82D'],
    photo: s7,
    id: 7,
    created: sub(new Date(), { days: 6, hours: 10, minutes: 0 }),
    description: chance.paragraph({ sentences: 2 }),
  },
  {
    title: 'Shoes for Girls',
    price: 300,
    discount: 80,
    related: false,
    salesPrice: 380,
    category: ['fashion', 'toys'],
    gender: 'Women',
    rating: 3,
    stock: true,
    qty: 1,
    colors: ['#1890FF', '#94D82D', '#FFC107'],
    photo: s8,
    id: 8,
    created: sub(new Date(), { days: 7, hours: 5, minutes: 20 }),
    description: chance.paragraph({ sentences: 2 }),
  },
  {
    title: 'Short & Sweet Purse',
    price: 175,
    discount: 25,
    related: false,
    salesPrice: 200,
    category: ['fashion'],
    gender: 'Women',
    rating: 3,
    stock: true,
    qty: 1,
    colors: ['#00AB55', '#000000'],
    photo: s9,
    id: 9,
    created: sub(new Date(), { days: 8, hours: 6, minutes: 20 }),
    description: chance.paragraph({ sentences: 2 }),
  },
  {
    title: 'Toy Dino for Fun',
    price: 210,
    discount: 40,
    related: false,
    salesPrice: 250,
    category: ['toys'],
    gender: 'Kids',
    rating: 3,
    stock: true,
    qty: 1,
    colors: ['#FFC0CB', '#FF4842'],
    photo: s10,
    id: 10,
    created: sub(new Date(), { days: 6, hours: 6, minutes: 20 }),
    description: chance.paragraph({ sentences: 2 }),
  },
  {
    title: 'Cute Soft Teddybear',
    price: 285,
    discount: 60,
    related: false,
    salesPrice: 345,
    category: ['toys'],
    gender: 'Kids',
    rating: 3,
    stock: true,
    qty: 1,
    colors: ['#FF4842', '#1890FF', '#94D82D'],
    photo: s11,
    id: 11,
    created: sub(new Date(), { days: 1, hours: 6, minutes: 20 }),
    description: chance.paragraph({ sentences: 2 }),
  },
  {
    title: 'Little Angel Toy',
    price: 5,
    discount: 5,
    related: false,
    salesPrice: 10,
    category: ['toys'],
    gender: 'Kids',
    rating: 3,
    stock: true,
    qty: 1,
    colors: ['#1890FF', '#94D82D', '#FFC107'],
    photo: s12,
    id: 12,
    created: sub(new Date(), { days: 9, hours: 6, minutes: 20 }),
    description: chance.paragraph({ sentences: 2 }),
  },
];

export default ProductsData;

let cartItems: any = [];

export const Ecommercehandlers = [
  //  Mock api endpoint to get products
  http.get('/api/data/eCommerce/ProductsData', () => {
    try {
      return HttpResponse.json({
        status: 200,
        msg: 'Success',
        data: ProductsData,
      });
    } catch (error) {
      return HttpResponse.json({
        status: 400,
        msg: 'Failed to fetch products',
        data: error,
      });
    }
  }),
  //  Mock api endpoint to get Cart item
  http.post('/api/eCommerce/carts', async () => {
    try {
      return HttpResponse.json({ status: 200, msg: 'success', data: cartItems });
    } catch (error) {
      return HttpResponse.json({ status: 400, msg: 'failed', error });
    }
  }),

  // Mock endpoint to add a product to the cart
  http.post('/api/data/eCommerce/add', async ({ request }) => {
    try {
      const { productId } = (await request.json()) as { productId: number };
      const productToAdd = ProductsData.find((product: any) => product.id === productId);
      if (!productToAdd) {
        return HttpResponse.json({ status: 400, msg: 'Product not found' });
      }
      const isItemInCart = cartItems.find(
        (cartItem: { id: any }) => cartItem.id === productToAdd?.id,
      );
      if (isItemInCart) {
        // if product available in the cart then update product to cartItems state
        let newItems = cartItems.map((cartItem: { id: any; qty: number }) =>
          cartItem.id === productToAdd?.id ? { ...cartItem, qty: cartItem.qty + 1 } : cartItem,
        );
        cartItems = newItems;
      } else {
        // Add the product to cartItems state
        cartItems.push({ ...productToAdd, qty: 1 });
      }

      return HttpResponse.json({ status: 200, msg: 'Success', data: cartItems });
    } catch (error) {
      return HttpResponse.json({
        status: 400,
        msg: 'Internal server error',
        data: error,
      });
    }
  }),

  // Mock endpoint to increment - decrementqty of a product in the cart
  http.put('/api/eCommerce/carts/increment-decrementqty', async ({ request }) => {
    try {
      const { id, action } = (await request.json()) as { id: any; action: any };
      const productToAdd = ProductsData.find((product: any) => product.id === id);
      if (!productToAdd) {
        return HttpResponse.json({ status: 400, msg: 'Product not found' });
      }
      if (action === 'Increment') {
        let newItems = cartItems.map((cartItem: { id: any; qty: number }) =>
          cartItem.id === productToAdd?.id ? { ...cartItem, qty: cartItem.qty + 1 } : cartItem,
        );
        cartItems = newItems;
      } else {
        let newItems = cartItems.map((cartItem: { id: any; qty: number }) =>
          cartItem.id === productToAdd?.id
            ? {
                ...cartItem,
                qty: cartItem.qty > 0 ? cartItem.qty - 1 : cartItem.qty,
              }
            : cartItem,
        );
        cartItems = newItems;
      }

      return HttpResponse.json({ status: 200, msg: 'Success', data: cartItems });
    } catch (error) {
      return HttpResponse.json({
        status: 400,
        msg: 'Internal server error',
        data: error,
      });
    }
  }),

  //Mock endpoint to remove an item from the cart
  http.delete('/api/eCommerce/remove-item-carts', async ({ request }) => {
    try {
      const { id } = (await request.json()) as { id: any };
      let remainingItems = cartItems.filter((product: any) => {
        return product.id !== id;
      });
      cartItems = remainingItems;
      return HttpResponse.json({ status: 200, msg: 'Success', data: cartItems });
    } catch (error) {
      return HttpResponse.json({
        status: 400,
        msg: 'Internal server error',
        error,
      });
    }
  }),
];
