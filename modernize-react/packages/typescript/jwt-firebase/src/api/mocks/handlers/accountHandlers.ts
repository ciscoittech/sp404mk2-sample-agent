import { sign, verify } from 'src/guards/jwt/Jwt';

import { http, HttpResponse } from 'msw';

const fakeRequest = (time: Date | any) => {
  return new Promise((res) => setTimeout(res, time));
};

interface userType {
  id: string;
  displayName: string;
  email: string;
  password: string;
  phoneNumber: string;
  country: string;
  address: string;
  state: string;
  city: string;
  zipCode: string;
  about: string;
  role: string;
  isPublic: boolean;
}

// ----------------------------------------------------------------------

const JWT_SECRET = 'wrap-secret-key';
const JWT_EXPIRES_IN = '2 days';

let users: userType[] = [
  {
    id: '8e5f29802-677d-772a-629a-7e5f298024da-0',
    displayName: 'Demo',
    email: 'demo1234@gmail.com',
    password: 'demo1234',
    phoneNumber: '+91 2166555',
    country: 'India',
    address: 'Khao galli',
    state: 'Delhi',
    city: 'Delhi',
    zipCode: '94116',
    about: 'Lorem ipsum hasellus viverra nulla ut metus varius laoreet. Phasellus tempus.',
    role: 'admin',
    isPublic: true,
  },
];

// ----------------------------------------------------------------------

interface LoginRequestBody {
  username: string;
  email: string;
  password: string;
}

export const accountHandlers = [
  http.get('api/user', () => {
    return HttpResponse.json([
      {
        id: 1,
        name: 'anson',
      },
    ]);
  }),

  http.post('/api/account/login', async ({ request }) => {
    try {
      await fakeRequest(1000);

      const { email, password } = (await request.json()) as LoginRequestBody;

      if (
        window.localStorage.getItem('users') !== undefined &&
        window.localStorage.getItem('users') !== null
      ) {
        const localUsers = window.localStorage.getItem('users');
        users = JSON.parse(localUsers!);
      }

      const user = users.find((_user) => _user.email === email);

      if (!user) {
        return HttpResponse.json([
          400,
          { message: 'There is no user corresponding to the email address.' },
        ]);
      }

      if (user.password !== password) {
        return HttpResponse.json([400, { message: 'Wrong password' }]);
      }

      const accessToken = sign({ userId: user.id }, JWT_SECRET, {
        expiresIn: JWT_EXPIRES_IN,
      });
      return HttpResponse.json([200, { accessToken, user }]);
    } catch (error) {
      console.error(error);
      return HttpResponse.json([500, { message: 'Internal server error' }]);
    }
  }),

  http.post('/api/account/register', async ({ request }: any) => {
    try {
      await fakeRequest(1000);

      const { email, password } = (await request.json()) as LoginRequestBody;
      let user = users.find((_user) => _user.email === email);
      const uid = new Date().toISOString();

      if (user) {
        return HttpResponse.json([
          400,
          { message: 'There already exists an account with the given email address.' },
        ]);
      }

      user = {
        id: uid,
        displayName: `${email}`,

        email,
        password,
        phoneNumber: '',
        country: '',
        address: '',
        state: '',
        city: '',
        zipCode: '',
        about: '',
        role: 'user',
        isPublic: true,
      };

      const accessToken = sign({ userId: user.id }, JWT_SECRET, {
        expiresIn: JWT_EXPIRES_IN,
      });
      return HttpResponse.json([200, { accessToken, user }]);
    } catch (error) {
      console.error(error);

      return HttpResponse.json([500, { message: 'Internal server error' }]);
    }
  }),

  http.get('/api/account/my-account', ({ request }: any) => {
    try {
      const { Authorization } = request.headers.get('Authorization');

      if (!Authorization) {
        return HttpResponse.json([401, { message: 'Authorization token missing' }]);
      }

      if (
        window.localStorage.getItem('users') !== undefined &&
        window.localStorage.getItem('users') !== null
      ) {
        const localUsers = window.localStorage.getItem('users');
        users = JSON.parse(localUsers!);
      }

      const accessToken = Authorization!.toString();
      const data = verify(accessToken, JWT_SECRET);
      const userId = typeof data === 'object' ? data?.userId : '';
      const user = users.find((_user) => _user.id === userId);

      if (!user) {
        return HttpResponse.json([401, { message: 'Invalid authorization token' }]);
      }

      return HttpResponse.json([200, { user }]);
    } catch (error) {
      console.error(error);

      return HttpResponse.json([500, { message: 'Internal server error' }]);
    }
  }),
];
