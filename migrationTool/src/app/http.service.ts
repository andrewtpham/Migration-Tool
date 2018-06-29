import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

@Injectable()
export class HttpService {
  private URL = 'http://localhost:5000/';

  constructor(private http: HttpClient) {
  }

  getOrganizations(endpoint) {
    return this.http.get(this.URL + endpoint).catch(err => this.handleErrorObservable(err));
  }

  getDataScheme(endpoint) {
    return this.http.get(this.URL + endpoint).catch(err => this.handleErrorObservable(err));
  }

  postMigrate(endpoint, data, organization) {
    const headers = new HttpHeaders();
    headers.append('Access-Control-Allow-Origin', '*');
    headers.append('Content-Type', 'application/json');
    const options = {headers: headers};
    const payload = {'mapping': data, 'organization': organization}
    this.http.post(this.URL + endpoint, payload, options).subscribe(
      res => {
        console.log(res);
      },
      err => {
        console.log(err);
      }
    );
  }

  private handleErrorObservable(error: Response | any) {
    console.error(error.message || error);
    return Observable.throw(error.message || error);
  }
}
