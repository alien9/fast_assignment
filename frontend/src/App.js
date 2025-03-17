//import logo from './logo.svg';
import './App.css';
import { v4 as uuidv4 } from 'uuid';
import { MapContainer, TileLayer, useMap, Polyline } from 'react-leaflet';
import { useEffect, useState } from 'react';
import 'leaflet/dist/leaflet.css';

function ChangeView({ center }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center);
  }, [map, center]);
  return null;
}

function App() {
  const [loading, setLoading] = useState(false);
  const [words, setWords] = useState([]);
  const [selectedWord, setSelected] = useState(null)
  const [position, setPosition] = useState([19.379086980151403, -99.13341507977586])
  const [roadPolys, setRoadPolys] = useState([])
  
  const upload = (event) => {
    const file = event.target.files[0];
    if (!file) {
      return;
    }
    setLoading(true);
    const id = uuidv4();
    let formData = new FormData();
    formData.append('file', file);
    formData.append('id', id)
    fetch('http://localhost:2000/upload/', { method: 'POST', body: formData }).then(async (d) => {
      setLoading(false);
    });
  }

  useEffect(() => {
    console.log('Lines updated in Map component via Context.', roadPolys);
  }, [roadPolys]);

  const clickRoad = (event) => {
    const wid = parseInt(event.target.id.match(/\d+$/).pop())
    setSelected(wid)
    document.getElementById("road_search").value = words[wid]
    drawRoad(words[wid])
    setWords([])
  }

  const drawRoad = (w) => {
    fetch(`http://localhost:2000/draw/${w}`, { method: 'GET' }).then(async (d) => {
      const data = await d.json();
      const lines = data.roads.map((ls) => ls.match(/^MULTILINESTRING \(\((.+)\)\)/).pop().split(/, /).map((c) => c.split(/\s/).reverse().map((d) => parseFloat(d))))
      setPosition(lines.map((pl) => pl.reduce((m, n) => [parseFloat(m[0]) + n[0], m[1] + n[1]]).map((o) => o / pl.length)).reduce((q, r) => [q[0] + r[0], q[1] + r[1]]).map((u) => u / lines.length))
      setRoadPolys(lines)
    });
  }

  const searchRoad = (event) => {
    switch (event.keyCode) {
      case 38:
        if (!selectedWord) setSelected(0)
        if (selectedWord > 0) setSelected(selectedWord - 1)
        break;
      case 40:
        if (selectedWord == null) setSelected(0)
        else
          if (selectedWord < words.length - 1) setSelected(selectedWord + 1)
        break
      case 13:
        if (selectedWord != null) {
          if (words[selectedWord])
            event.target.value = words[selectedWord]
          drawRoad(words[selectedWord])
        }
        setWords([])
        break
      default:
        if(event.target.value.length<3) return
        fetch(`http://localhost:2000/search/?t=${event.target.value}`, { method: 'GET' }).then(async (d) => {
          setLoading(false)
          setSelected(null)
          const data = await d.json();
          setWords(data.words)
        });
    }
  }
  const color = { color: 'red' }
  return (
    <div className="relative">
      <div className="max-w-md mx-auto p-2 -z-50">
        <div id="hs-combobox-json-example-based-on-api-pathes" className="relative">
        <label>Search:</label>
          <div className="relative">
            
            <input id="road_search" className="py-2.5 sm:py-3 ps-4 pe-9 block w-full border-gray-200 rounded-lg sm:text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400 dark:placeholder-neutral-500 dark:focus:ring-neutral-600" type="text" role="combobox" aria-expanded="false" data-hs-combo-box-input="" onKeyUp={searchRoad} />
            <div className="absolute top-1/2 end-3 -translate-y-1/2" aria-expanded="false" role="button" data-hs-combo-box-toggle="">
              <svg className="shrink-0 size-3.5 text-gray-500 dark:text-neutral-500" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m7 15 5 5 5-5"></path>
                <path d="m7 9 5-5 5 5"></path>
              </svg>
            </div>
          </div>
          <div id="listbox" className="absolute z-50 w-full max-h-72 p-1 bg-white border border-gray-200 rounded-lg overflow-hidden overflow-y-auto [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-track]:bg-gray-100 [&::-webkit-scrollbar-thumb]:bg-gray-300 dark:[&::-webkit-scrollbar-track]:bg-neutral-700 dark:[&::-webkit-scrollbar-thumb]:bg-neutral-500 dark:bg-neutral-900 dark:border-neutral-700" style={{ display: (words.length) ? 'block' : 'none' }} role="listbox" data-hs-combo-box-output="">
            {words.map((item, index) => (
              <div className={`flex justify-between items-center p-2 w-full cursor-pointer ${(selectedWord === index) ? "bg-blue-800 text-white" : "bg-white"}`} key={`words_${index}`} onClick={clickRoad} id={`list_words_${index}`}>{item}</div>
            ))}
          </div>
        </div>
      </div>


      <div className="relative bg-black"><div className="relative h-96 z-0">
        <MapContainer className="h-full" center={position} zoom={16} scrollWheelZoom={true}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <ChangeView center={position} zoom={13} />
          {roadPolys.map((r, index) => 
            <Polyline pathOptions={color} positions={r} key={index} />
          )}
        </MapContainer>
      </div></div>

      <div className="App p-8 w-1/2">
        <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white" htmlFor="file_input">Upload files</label>
        <input
          onChange={upload}
          className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" id="file_input" type="file" />
      </div>

      {loading &&
        <div className="text-center m-4">
          <div role="status">
            <svg aria-hidden="true" className="inline w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
              <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
            </svg>
            <span className="sr-only">Loading...</span>
          </div>
        </div>
      }

    </div>


  );
}

export default App;
