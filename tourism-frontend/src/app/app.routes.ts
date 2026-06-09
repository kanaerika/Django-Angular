import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home';
import { Login } from './pages/login/login';
import { Register } from './pages/register/register';
import { Dashboard } from './pages/dashboard/dashboard';
import { DestinationDetails } from './pages/destination-details/destination-details';
import { BookingComponent } from './pages/booking/booking.component';
export const routes: Routes = [
  {
    path: '',
    component: HomeComponent
  },
  {
    path: 'login',
    component: Login
  },
  {
    path: 'register',
    component: Register
  },
  {
    path: 'signup',
    component: Register
  },
  {
    path: 'create-account',
    component: Register
  },
  {
    path: 'home',
    component: HomeComponent
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./pages/dashboard/dashboard')
      .then(m => m.Dashboard)
  },
   {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  {
    path: 'destination/:id',
    loadComponent: () =>
      import('./pages/destination-details/destination-details')
      .then(m => m.DestinationDetails)
  },
  { path: 'booking', component: BookingComponent }
];