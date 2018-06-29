import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgSelectModule } from '@ng-select/ng-select';
import { HttpClientModule } from '@angular/common/http';
import { BrowserModule } from '@angular/platform-browser';
import { BsDropdownModule } from 'ngx-bootstrap/dropdown';
import { NgxDatatableModule } from '@swimlane/ngx-datatable';

import { HttpService } from './http.service';
import { AppComponent } from './app.component';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BsDropdownModule.forRoot(),
    BrowserModule,
    NgxDatatableModule,
    HttpClientModule,
    FormsModule,
    NgSelectModule
  ],
  providers: [HttpService],
  bootstrap: [AppComponent],
})
export class AppModule {
}
