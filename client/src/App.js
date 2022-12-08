import './App.css';
import './index.css'
import * as React from 'react';
import ColorToggleButton from './components/toggle'
import InputComponent from "./components/inputComponent";
import {useEffect, useRef, useState} from "react";
function App(){

    const canvasRef = useRef(null);
    const contextRef = useRef(null);
    const [point1, point1State] = useState(null)
    const [point2, point2State] = useState(null)
    const [dataRoads, dataRoadsState] = useState(null)
    const [dataRoutes, dataRoutesState] = useState(null)
    const countCars = useRef(null);
    const radius = useRef(null);
    const isRadius = useRef(null);
    const [msg, msgState] = useState("")
    const typeRoads = useRef(null)
    const address =useRef(null)
    const minWorkload = useRef(null)
    const maxWorkload = useRef(null)
    const minLenght = useRef(null)
    const maxLenght = useRef(null)
    const minTime = useRef(null)
    const maxTime = useRef(null)
    const fileName = useRef(null)
    const [isOpen,isOpenState] = useState(false)
    const [roadsMaxCount, roadsMaxCountState] = useState(null)
    const [routesMaxCount, routesMaxCountState] = useState(null)
    const [currentDrawRouteId, currentDrawRouteIdState] = useState(null)
    const [mapImage, mapImageState] = useState(null)
    useEffect(() => {
        document.body.style.cursor='wait';
        const canvas = canvasRef.current;
        canvas.width = 830;
        canvas.height = 830;
        const context = canvas.getContext("2d");
        context.lineCap = "round";
        context.strokeStyle = "blue";
        context.lineWidth = 8;
        contextRef.current = context;
        let image_new = new Image()
        image_new.src = '/map_image'
        image_new.onload = function() {
            mapImageState(image_new)
            contextRef.current.drawImage(image_new, 0, 0, 830, 830)
            document.body.style.cursor='default';
        }
    }, []);
    const startDrawing = ({nativeEvent}) => {
        const {offsetX, offsetY} = nativeEvent;
        console.log(offsetX, offsetY)
        if(point1 === null){
            contextRef.current.beginPath();
            contextRef.current.moveTo(offsetX, offsetY);
            contextRef.current.lineTo(offsetX, offsetY);
            contextRef.current.stroke();
            point1State([offsetX, offsetY])
        }
        else if(point2 === null){
            contextRef.current.beginPath();
            contextRef.current.moveTo(offsetX, offsetY);
            contextRef.current.lineTo(offsetX, offsetY);
            contextRef.current.stroke();
            point2State([offsetX, offsetY])
        }
        console.log(point1, point2)
        nativeEvent.preventDefault();
    };
    function getPoints(){
        if(point2 != null && point1 != null){
            console.log(point1, point2);
            contextRef.current.beginPath();
            contextRef.current.moveTo(point1[0], point1[1]);
            contextRef.current.lineTo(point1[0], point1[1]);
            contextRef.current.stroke();
            contextRef.current.beginPath();
            contextRef.current.moveTo(point2[0], point2[1]);
            contextRef.current.lineTo(point2[0], point2[1]);
            contextRef.current.stroke();
        }
    }
    function getImage(flag = true, f = ()=>{}){
        let image_new = new Image()
        image_new.src = '/map_image?' + new Date().getTime()
        image_new.onload = function() {
            mapImageState(image_new)
            contextRef.current.drawImage(image_new, 0, 0, 830, 830)
            if(flag){
                getPoints();
                console.log(flag, '2')
                f()
            }
        }
        console.log("img")
    }
    function getSavedImage(flag = true, f = ()=>{}){
        contextRef.current.drawImage(mapImage, 0, 0, 830, 830)
        if(flag){
            getPoints();
            console.log(flag, '2')
            f()
        }
    }
    function dropPoints(){
        console.log(5)
        contextRef.current.globalCompositeOperation = 'destination-out';
        contextRef.current.lineWidth=10
        if(point1 != null){
            contextRef.current.lineTo(point1[0], point1[1]);
            contextRef.current.stroke()
            point1State(null)
        }
        if(point2 != null){
            contextRef.current.lineTo(point2[0], point2[1]);
            contextRef.current.stroke()
            point2State(null)
        }
        contextRef.current.lineWidth=8
        contextRef.current.globalCompositeOperation = 'source-over';
        getImage(false);
    }
    function getRoads(){
        fetch('/roads').then(response=>response.json())
            .then((json) => {
                dataRoadsState(json)
                roadsMaxCountState(json.length)
            })
    }
    function getRoutes(){
        fetch('/routes').then(response=>response.json())
            .then((json) => {
                dataRoutesState(json)
                routesMaxCountState(json.length)
            })
    }
    function drawRoutes(id, alwaysDraw=false){
        if(dataRoutes === null){
            return
        }
        console.log('2',id, currentDrawRouteId)
        getSavedImage(true, ()=>{
            if(id === null){
                return
            }
            console.log("checking draw rotues")
            if(!alwaysDraw && currentDrawRouteId === id){
                currentDrawRouteIdState(null)
                return
            }
            currentDrawRouteIdState(id)
            contextRef.current.moveTo(point1[0], point1[1])
            contextRef.current.lineWidth = 2
            for(let i = 0; i < dataRoutes[id].points.length; i++){
                drawLine(dataRoutes[id].points[i][0], dataRoutes[id].points[i][1])
            }
            drawLine(point2[0], point2[1])
            contextRef.current.lineWidth=8
        })


    }
    function drawLine(x,y) {
        contextRef.current.lineTo(x, y);
        contextRef.current.stroke()
    }

    //+ new URLSearchParams({
    //     foo: 'value',
    //     bar: 2,
    // })
    function filterRoads(ev){
        console.log(address.current.value)
        console.log(minWorkload.current.value)
        console.log(maxWorkload.current.value)
        console.log(typeRoads.current.value)
        let url_params = {}
        if(minWorkload.current.value !== ""){
            url_params["min"] = minWorkload.current.value
        }
        if(maxWorkload.current.value !== ""){
            url_params["max"] = maxWorkload.current.value
        }
        if(address.current.value !== ""){
            url_params["address"] = address.current.value
        }
        if(typeRoads.current.value !== ""){
            url_params["type"] = typeRoads.current.value
        }
        msgState("")
        fetch('/roads?'+new URLSearchParams(url_params))
            .then(response=>response.json())
            .then((json) => {
                console.log(json)
                dataRoadsState(json)
            })
        ev.preventDefault();
    }
    function filterRoutes(ev){
        console.log(minLenght.current.value)
        console.log(maxLenght.current.value)
        console.log(minTime.current.value)
        console.log(maxTime.current.value)
        let url_params = {}
        if(minLenght.current.value !== ""){
            url_params["minLength"] = minLenght.current.value * 1000
        }
        if(maxLenght.current.value !== ""){
            url_params["maxLength"] = maxLenght.current.value * 1000
        }
        if(minTime.current.value !== ""){
            url_params["minTime"] = minTime.current.value
        }
        if(maxTime.current.value !== ""){
            url_params["maxTime"] = maxTime.current.value
        }
        msgState("")
        fetch('/routes?'+new URLSearchParams(url_params))
            .then(response=>response.json())
            .then(json => dataRoutesState(json))
        ev.preventDefault();
    }
    function simulate(ev){
        ev.preventDefault()
        console.log( point1[0], point1[1], point2[0], point2[1], radius.current.value,countCars.current.value)
        console.log('ee');
        console.log(point1 == null || point2 == null)
        if(point1 == null || point2 == null){
            msgState("Не указаны точки маршрута");
        }
        else{
            msgState("")
            console.log(2, 'radius.current.value',Number(radius.current.value)/1000)
            fetch("/simulate", {
                method: 'POST',
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "point1": {
                        "x": point1[0],
                        "y": point1[1]
                    },
                    "point2": {
                        "x": point2[0],
                        "y": point2[1]
                    },
                    "radius": Number(radius.current.value)/1000,
                    "car_count": countCars.current.value
                })
            }).then((responce)=>{
                console.log(responce);
                getImage();
                getPoints();
                getRoads();
                getRoutes();
                currentDrawRouteIdState(null)
            })
        }

    }
    function getCountRoutes(){
        if(dataRoutes == null){
            return (<p>Количество маршрутов: {0}</p>)
        }
        return (<p>Количество маршрутов: {dataRoutes.length}</p>)
    }
    function importFile(){
        console.log('Import',fileName.current.files[0])
        if(fileName.current.value === ''){
            msgState('Название файла остутсвует')
        }
        else{
            let formData = new FormData();
            formData.append("import", fileName.current.files[0]);
            document.body.style.cursor='wait';
            fetch('/import', {method: "POST", body: formData
            }).then((response) => {
                if(response.ok === false){
                    alert("Импортируемые данные содержат ошибку")
                }else{
                    getImage();
                    getPoints();
                    getRoads();
                    getRoutes();
                }
                document.body.style.cursor='default';
                msgState('');
                isOpenState(false);
            });
        }
    }
    function exportFile(){
        fetch('/export').then((result) => {
            return result.blob();
        }).then((blob) => {
            if (blob != null) {
                var url = window.URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.href = url;
                a.download = 'export.json';
                document.body.appendChild(a);
                a.click();
                a.remove();
            }
        });
    }
    return(
        <div className="App">

            <div className="left">
                <button>Справка</button>
                <button onClick={()=>{
                isOpenState(true)
                }
                }>Import</button>
                <button onClick={exportFile}>Export</button>
            </div>
            <div className={`flex middle center  ${isOpen ? "modal open" : ""}`}>
            {isOpen ?
                (<div className={`row modal-content`}>
                    <div className="col-12 middle modal-title">Выберите файл</div>
                    {msg}
                    <br/>
                    <input ref={fileName} type={"file"} placeholder={"Название файла"}/>
                    <br/>
                    <button onClick={importFile}>Import</button>
                    <button onClick={()=>{
                        isOpenState(false)
                    }}>Закрыть</button>
                </div>) : null
            }
            </div>
            <div>
            <div className="right">
                <p>{msg}</p>
                <div className="inline">
                    <InputComponent value={0} label={"Количество машин"} type={"number"}
                                    onChange={() => console.log(1)} sRef={countCars}/>
                    <InputComponent value={false} label={"Радиус поиска маршрутов"} variant={"input"}
                                    type={"checkbox"} sRef={isRadius}/>

                </div>
                <input min={1} max={1000} step={1} type={"range"} name={"radius"} ref={radius}/>
                <div className="inline">
                    <button onClick={simulate}>Смоделировать</button>
                    <button onClick={(e)=>{
                        fetch("/clear", {
                            method: "DELETE"
                        }).then((response) =>{
                            dropPoints()
                            dataRoutesState(null);
                            dataRoadsState(null);
                            currentDrawRouteIdState(null);
                        })
                        }}>Очистить точки на карте</button>
                </div>
                {getCountRoutes()}
                <br/>
                <ColorToggleButton typeRoads={typeRoads} address={address} minWorkload={minWorkload} maxWorkload={maxWorkload} minLenght={minLenght} maxLenght={maxLenght} minTime={minTime} maxTime={maxTime} filterRoads={filterRoads} filterRoutes={filterRoutes} dataRoads={dataRoads} dataRoutes={dataRoutes} drawRoutes={drawRoutes} roadsMaxCount={roadsMaxCount} routesMaxCount={routesMaxCount} curDrawRouteId={currentDrawRouteId}/>
            </div>
            <div align="center">
                <div class="table">
                    <div class="row">
                        <div class="cell">
                            <canvas className="map"
                                    ref={canvasRef}
                                    onMouseDown={startDrawing}
                            >
                            </canvas>

                        </div>
                    </div>
                </div>
            </div>
            </div>
        </div>
    )
}

export default App;
